from __future__ import annotations

import contextlib
import functools
import html as html_lib
import http.server
import json
import re
import shutil
import socketserver
import subprocess
import threading
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

import pytest
from mike.versions import Versions

ROOT = Path(__file__).resolve().parents[2]


def _load_macros():
    import importlib.util

    module_name = "test_macros_module"
    module_path = ROOT / "macros.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


macros = _load_macros()
project_version = macros.project_version


def _load_release_version() -> str:
    return project_version()


_RELEASE_VERSION = _load_release_version()


def _write_temp_config(*, site_url: str, site_dir: Path, token: str) -> Path:
    lines: list[str] = []
    for line in (ROOT / "mkdocs.yml").read_text(encoding="utf-8").splitlines():
        if line.startswith("site_url:"):
            lines.append(f"site_url: {site_url}")
        elif line.startswith("docs_dir:"):
            lines.append("docs_dir: docs-src")
        elif line.startswith("site_dir:"):
            lines.append(f"site_dir: {site_dir}")
        else:
            lines.append(line)

    config = ROOT / f"mkdocs.unit-macros.{token}.yml"
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config


def _build_docs_with_config(config_path: Path) -> None:
    subprocess.run(
        [
            "uv",
            "run",
            "--frozen",
            "zensical",
            "build",
            "--config-file",
            str(config_path),
            "--strict",
            "--clean",
        ],
        cwd=ROOT,
        check=True,
    )


def _read_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_badge_texts(html: str) -> list[str]:
    block_re = re.compile(
        r'<span[^>]*class="[^"]*md-version__current[^"]*"[^>]*>(.*?)</span>',
        re.DOTALL,
    )
    return [
        html_lib.unescape(re.sub(r"<[^>]+>", "", match)).strip()
        for match in block_re.findall(html)
    ]


def _extract_json_script(html: str, script_id: str) -> dict[str, Any]:
    marker = 'id="__shelfdb-version-behavior-probe"'
    start = html.find(marker)
    if start < 0:
        raise AssertionError(f"missing script #{script_id}")

    start = html.rfind("<", 0, start)
    if start < 0:
        raise AssertionError(f"missing script #{script_id}")

    match = list(
        re.finditer(
            r'<div[^>]*id="__shelfdb-version-behavior-probe"[^>]*>([\s\S]*?)</div>',
            html[start:],
            re.DOTALL,
        )
    )
    if not match:
        raise AssertionError(f"missing script #{script_id}")

    return json.loads(html_lib.unescape(match[-1].group(1).strip()))


def _copy_site_tree(source_root: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        source_root,
        target,
        dirs_exist_ok=False,
        ignore=shutil.ignore_patterns("shelfdb"),
    )


def _build_release_layout(site_dir: Path, *, version: str) -> None:
    release_root = ROOT / site_dir / "shelfdb"
    _copy_site_tree(ROOT / site_dir, release_root / version)
    _copy_site_tree(ROOT / site_dir, release_root / "latest")
    _write_versions_json(site_dir, version)


def _remove_if_empty(path: Path) -> None:
    try:
        if path.exists() and path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def _rendered_docs(
    tmp_path: Path,
    *,
    site_url: str,
    suffix: str,
    with_shelfdb_release_layout: bool = False,
):
    site_dir = Path(f".tmp-macros-build/{tmp_path.name}/{suffix}")
    config = _write_temp_config(
        site_url=site_url,
        site_dir=site_dir,
        token=f"{tmp_path.name}.{suffix.replace('.', '-')}",
    )
    _build_docs_with_config(config)

    if with_shelfdb_release_layout:
        _build_release_layout(site_dir, version=_RELEASE_VERSION)

    try:
        yield site_dir
    finally:
        tmp_parent = ROOT / site_dir.parent
        shared_root = ROOT / ".tmp-macros-build"
        shutil.rmtree(tmp_parent, ignore_errors=True)
        _remove_if_empty(tmp_parent)
        _remove_if_empty(shared_root)
        if config.exists():
            config.unlink()


def _real_mike_versions_json(version: str) -> str:
    versions = Versions()
    versions.add(version, title=f"v{version}", aliases=["latest"])
    versions.add("development", title="development")
    return versions.dumps()


def _write_versions_json(site_dir: Path, version: str) -> None:
    (ROOT / site_dir / "shelfdb" / "versions.json").write_text(
        _real_mike_versions_json(version) + "\n",
        encoding="utf-8",
    )


@contextlib.contextmanager
def _http_server(site_dir: Path):
    class _NoLogHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - stdlib override
            return

    class _ReusableServer(socketserver.TCPServer):
        allow_reuse_address = True

    handler = functools.partial(
        _NoLogHandler, directory=str((ROOT / site_dir).resolve())
    )
    server = _ReusableServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _inject_probe_script(html: str) -> str:
    return html.replace(
        "</body>",
        """
    <script>
    (() => {
      const pickText = (node) => (node && node.textContent ? node.textContent.trim() : null);
      const rect = (node) => {
        if (!node) return null;
        const bounds = node.getBoundingClientRect();
        return {
          x: bounds.x,
          y: bounds.y,
          right: bounds.right,
          bottom: bounds.bottom,
          width: bounds.width,
          height: bounds.height,
        };
      };
      const overlap = (a, b) => {
        if (!a || !b) return false;
        return !(
          a.x + a.width <= b.x ||
          b.x + b.width <= a.x ||
          a.y + a.height <= b.y ||
          b.y + b.height <= a.y
        );
      };
      const isVisible = (node) => {
        if (!node) return false;
        const styles = window.getComputedStyle(node);
        if (styles.display === 'none' || styles.visibility === 'hidden') return false;
        const opacity = parseFloat(styles.opacity || '1');
        if (!Number.isNaN(opacity) && opacity <= 0) return false;
        const bounds = rect(node);
        return !!(bounds && bounds.width > 0 && bounds.height > 0);
      };
      const collect = () => {
        const allVersions = Array.from(document.querySelectorAll('.md-version'));
        const staticNode = allVersions.find((node) => node.classList.contains('md-version--static'));
        const nativeNode = allVersions.find((node) => !node.classList.contains('md-version--static'));
        const titleNode = document.querySelector('.md-header__topic .md-ellipsis');
        const visibleNodes = allVersions.filter(isVisible);
        const nativeText = pickText(nativeNode?.querySelector('.md-version__current'));
        const report = {
          badgeCount: allVersions.length,
          visibleBadgeCount: visibleNodes.length,
          staticVisible: isVisible(staticNode),
          nativeVisible: isVisible(nativeNode),
          staticText: pickText(staticNode?.querySelector('.md-version__current')),
          nativeText: nativeText,
          staticRect: rect(staticNode),
          titleRect: rect(titleNode),
          nativeRect: rect(nativeNode),
          overlapStaticWithTitle: overlap(rect(staticNode), rect(titleNode)),
          nativeHref: (() => {
            const selected = nativeText;
            const candidates = nativeNode?.querySelectorAll?.('a') || [];
            for (const anchor of candidates) {
              if ((anchor.textContent || '').trim() === selected) {
                return anchor.getAttribute('href');
              }
            }
            return null;
          })(),
          hasNative: !!nativeNode,
        };
        const probe = document.createElement('div');
        probe.id = '__shelfdb-version-behavior-probe';
        probe.style.display = 'none';
        probe.textContent = JSON.stringify(report);
        document.body.appendChild(probe);
      };
      collect();
      setTimeout(collect, 750);
    })();
    </script>
    </body>""",
    )


def _require_chrome_binary() -> str:
    chrome = (
        shutil.which("google-chrome")
        or shutil.which("chromium")
        or shutil.which("google-chrome-stable")
    )
    if chrome is None:
        pytest.fail(
            "Chrome-compatible browser binary required for version-selector assertions. "
            "Install google-chrome or chromium and retry (checked: google-chrome, chromium, google-chrome-stable)."
        )
    return cast(str, chrome)


def _probe_with_chrome(site_dir: Path, *, path: str = "/") -> dict[str, Any]:
    chrome = _require_chrome_binary()

    path = path.strip()
    path = "/" if not path else (path if path.startswith("/") else f"/{path}")

    if path.endswith("/"):
        target_path = ROOT / site_dir / path.lstrip("/") / "index.html"
    else:
        target_path = ROOT / site_dir / path.lstrip("/")
    if target_path.is_dir():
        target_path = target_path / "index.html"

    index_path = ROOT / site_dir / "index.html"
    if target_path.is_dir() or not target_path.exists():
        if target_path.suffix:
            raise AssertionError(
                f"Missing expected rendered file for browser probe: {target_path}"
            )
        candidate = target_path.with_suffix(".html")
        if candidate.exists():
            target_path = candidate
        else:
            target_path = index_path

    original = _read_html(target_path)
    try:
        with _http_server(site_dir) as port:
            base = f"http://127.0.0.1:{port}{path}"
            if not base.endswith("/"):
                base = f"{base}/"

            patched = original
            patched = patched.replace('"alias":true', '"alias":false')
            patched = patched.replace('"base":"."', f'"base":"{base}"')
            patched = patched.replace('"base":".."', f'"base":"{base}"')
            patched = patched.replace(
                '"base":"/"',
                f'"base":"{base}"',
            )

            target_path.write_text(_inject_probe_script(patched), encoding="utf-8")

            url = f"http://127.0.0.1:{port}{path}"
            result = subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--virtual-time-budget=2500",
                    "--enable-logging=stderr",
                    "--dump-dom",
                    url,
                ],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
    finally:
        target_path.write_text(original, encoding="utf-8")

    output = result.stdout
    if isinstance(output, (bytes, bytearray)):
        output = output.decode("utf-8")
    return _extract_json_script(output, "__shelfdb-version-behavior-probe")


def test_project_version_reads_pyproject() -> None:
    assert project_version() == _RELEASE_VERSION


def test_rendered_link_uses_published_asset_for_local_docs(tmp_path) -> None:
    with _rendered_docs(
        tmp_path, site_url="https://keenlycode.github.io/shelfdb/", suffix="local-site"
    ) as site_dir:
        html = _read_html(ROOT / site_dir / "index.html")

        assert "version-badge.css" in html
        assert (ROOT / site_dir / "assets/stylesheets/version-badge.css").exists()


def test_rendered_version_markup_is_accessible_and_local_context(tmp_path) -> None:
    with _rendered_docs(
        tmp_path,
        site_url="https://keenlycode.github.io/shelfdb/",
        suffix="local-site",
    ) as site_dir:
        html = _read_html(ROOT / site_dir / "index.html")

        assert 'class="no-js"' in html
        assert not (ROOT / site_dir / "versions.json").exists()

        assert html.count('data-md-component="version-badge"') == 1
        assert "md-version--development" in html
        assert "md-version--release" not in html
        assert 'aria-label="Current documentation version"' in html
        assert 'aria-live="polite" aria-atomic="true"' in html
        assert _extract_badge_texts(html)[0] == "development"


def test_no_js_release_and_latest_contexts_show_version_derived_labels(
    tmp_path,
) -> None:
    for suffix in (_RELEASE_VERSION, "latest"):
        with _rendered_docs(
            tmp_path,
            site_url=f"https://keenlycode.github.io/shelfdb/{_RELEASE_VERSION}/",
            suffix=f"{suffix}-site",
            with_shelfdb_release_layout=True,
        ) as site_dir:
            html = _read_html(ROOT / site_dir / "shelfdb" / suffix / "index.html")

            assert _extract_badge_texts(html)[0] == f"v{_RELEASE_VERSION}"
            assert "md-version--release" in html
            assert "md-version--development" not in html


@pytest.mark.parametrize("target", ["release", "latest"])
def test_headless_browser_confirms_native_selector_uses_real_manifest(
    tmp_path, target: str
) -> None:
    suffix = _RELEASE_VERSION if target == "release" else "latest"
    with _rendered_docs(
        tmp_path,
        site_url=f"https://keenlycode.github.io/shelfdb/{_RELEASE_VERSION}/",
        suffix=f"{target}-native",
        with_shelfdb_release_layout=True,
    ) as site_dir:
        probe = _probe_with_chrome(site_dir, path=f"/shelfdb/{suffix}/")

        assert probe["badgeCount"] == 2
        assert probe["visibleBadgeCount"] == 1
        assert probe["hasNative"]
        assert probe["nativeVisible"]
        assert not probe["staticVisible"]
        assert probe["nativeText"] == f"v{_RELEASE_VERSION}"
        assert (
            urlparse(probe["nativeHref"] or "").path == f"/shelfdb/{_RELEASE_VERSION}/"
        )
        assert not probe["overlapStaticWithTitle"]


def test_headless_browser_confirms_local_js_fallback_has_single_visible_control(
    tmp_path,
) -> None:
    with _rendered_docs(
        tmp_path,
        site_url="https://keenlycode.github.io/shelfdb/",
        suffix="local-native-missing",
    ) as site_dir:
        probe = _probe_with_chrome(site_dir)

        assert probe["badgeCount"] == 1
        assert probe["visibleBadgeCount"] == 1
        assert not probe["hasNative"]
        assert probe["staticVisible"]
        assert probe["staticText"] == "development"
        assert not probe["overlapStaticWithTitle"]


def test_rendered_docs_config_points_to_version_assets() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "custom_dir: overrides" in mkdocs
    assert "assets/stylesheets/version-badge.css" in mkdocs
    assert "version_selector_fallback" in mkdocs
    assert "version_control_label" not in mkdocs
