import importlib.util
import io
import tarfile
import uuid
import zipfile
from pathlib import Path
import sys

import pytest


def load_release_module():
    module_name = "test_release_module"
    module_path = Path(__file__).resolve().parents[2] / "dev" / "release.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


release = load_release_module()


def write_artifacts(dist, *, version="3.0.1"):
    metadata = f"Name: shelfdb\nVersion: {version}\n\n".encode()

    wheel = dist / f"shelfdb-{version}-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(f"shelfdb-{version}.dist-info/METADATA", metadata)

    sdist = dist / f"shelfdb-{version}.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        info = tarfile.TarInfo(f"shelfdb-{version}/PKG-INFO")
        info.size = len(metadata)
        archive.addfile(info, io.BytesIO(metadata))

    return wheel, sdist


def test_zensical_build_command_defaults_to_strict_clean():
    assert release.zensical_build_command(config_file=Path("mkdocs.yml")) == [
        "uv",
        "run",
        "zensical",
        "build",
        "--config-file",
        "mkdocs.yml",
        "--strict",
        "--clean",
    ]


def test_zensical_build_config_with_isolated_output_rewrites_only_site_dir(tmp_path):
    source = tmp_path / "mkdocs.yml"
    source.write_text(
        "site_name: ShelfDB\nsite_dir: docs\ndocs_dir: docs-src\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / ".release-site-abc"

    config_path = release.zensical_build_config_with_isolated_output(
        source_config=source, output_dir=output_dir
    )

    config_text = config_path.read_text(encoding="utf-8")
    assert f"site_dir: {output_dir}" in config_text
    assert "docs_dir: docs-src" in config_text
    assert config_text.count("site_dir:") == 1
    assert config_path.exists()


def test_zensical_build_config_with_isolated_output_raises_without_site_dir(tmp_path):
    source = tmp_path / "mkdocs.yml"
    source.write_text("site_name: ShelfDB\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Expected to replace top-level site_dir"):
        release.zensical_build_config_with_isolated_output(
            source_config=source, output_dir=tmp_path / "out"
        )


def test_verify_artifacts_returns_valid_wheel(tmp_path):
    expected_artifacts = write_artifacts(tmp_path)

    artifacts = release.verify_artifacts(tmp_path, "3.0.1")

    assert artifacts == expected_artifacts


def test_verify_artifacts_rejects_wrong_version(tmp_path):
    write_artifacts(tmp_path, version="3.0.0")

    with pytest.raises(RuntimeError, match="expected"):
        release.verify_artifacts(tmp_path, "3.0.1")


def test_check_github_alerts_accepts_zero_alerts(tmp_path, monkeypatch):
    monkeypatch.setattr(
        release.subprocess, "check_output", lambda *args, **kwargs: "0\n"
    )

    release.check_github_alerts(tmp_path)


def test_run_release_checks_exports_without_mike_then_runs_strict_audit(
    monkeypatch, tmp_path
):
    root = tmp_path
    root.joinpath("mkdocs.yml").write_text("site_name: ShelfDB\nsite_dir: docs\n")
    commands: list[tuple[tuple[str, ...], Path]] = []

    def fake_run_command(command: list[str], *, cwd: Path) -> None:
        commands.append((tuple(command), cwd))

    monkeypatch.setattr(release, "run_command", fake_run_command)
    monkeypatch.setattr(
        release,
        "verify_artifacts",
        lambda dist_dir, expected_version: (dist_dir / "wheel", dist_dir / "sdist"),
    )
    monkeypatch.setattr(release, "venv_python", lambda venv: venv / "bin" / "python")

    release.run_release_checks(root, "3.0.1")

    export_call = next(cmd for cmd, _ in commands if cmd[:2] == ("uv", "export"))
    assert "--no-emit-package" in export_call
    assert export_call[export_call.index("--no-emit-package") + 1] == "mike"

    audit_call = next(
        cmd
        for cmd, _ in commands
        if cmd[:2] == ("uvx", f"pip-audit=={release.PIP_AUDIT_VERSION}")
    )
    assert "--strict" in audit_call

    build_calls = [
        command
        for command, _ in commands
        if command[:4] == ("uv", "run", "zensical", "build")
    ]
    assert len(build_calls) == 1
    assert "--strict" in build_calls[0]
    assert "--clean" in build_calls[0]
    assert "--config-file" in build_calls[0]


def test_run_release_checks_cleans_isolated_config_and_site_dir_on_build_failure(
    monkeypatch, tmp_path
):
    root = tmp_path
    root.joinpath("mkdocs.yml").write_text("site_name: ShelfDB\nsite_dir: docs\n")
    root.joinpath("docs").mkdir()
    root.joinpath("docs", "keep.txt").write_text("keep")

    commands: list[tuple[tuple[str, ...], Path]] = []
    deterministic_uuid = uuid.UUID(int=0)
    expected_site_dir = root / f".release-site.{deterministic_uuid.hex}"
    expected_config = root / f"mkdocs.release.{deterministic_uuid.hex}.yml"

    expected_site_dir.mkdir()

    def fake_run_command(command: list[str], *, cwd: Path) -> None:
        commands.append((tuple(command), cwd))
        if command[:4] == ["uv", "run", "zensical", "build"]:
            raise RuntimeError("build failed")

    monkeypatch.setattr(release.uuid, "uuid4", lambda: deterministic_uuid)
    monkeypatch.setattr(release, "run_command", fake_run_command)
    monkeypatch.setattr(
        release,
        "verify_artifacts",
        lambda dist_dir, expected_version: (dist_dir / "wheel", dist_dir / "sdist"),
    )
    monkeypatch.setattr(release, "venv_python", lambda venv: venv / "bin" / "python")

    with pytest.raises(RuntimeError, match="build failed"):
        release.run_release_checks(root, "3.0.1")

    assert not expected_config.exists()
    assert not expected_site_dir.exists()
    assert root.joinpath("docs", "keep.txt").exists()


def test_run_release_checks_cleans_isolated_config_and_site_dir_on_success(
    monkeypatch, tmp_path
):
    root = tmp_path
    root.joinpath("mkdocs.yml").write_text("site_name: ShelfDB\nsite_dir: docs\n")
    root.joinpath("docs").mkdir()
    root.joinpath("docs", "keep.txt").write_text("keep")

    commands: list[tuple[tuple[str, ...], Path]] = []
    deterministic_uuid = uuid.UUID(int=1)
    expected_site_dir = root / f".release-site.{deterministic_uuid.hex}"
    expected_config = root / f"mkdocs.release.{deterministic_uuid.hex}.yml"

    expected_site_dir.mkdir()

    def fake_run_command(command: list[str], *, cwd: Path) -> None:
        commands.append((tuple(command), cwd))

    monkeypatch.setattr(release.uuid, "uuid4", lambda: deterministic_uuid)
    monkeypatch.setattr(release, "run_command", fake_run_command)
    monkeypatch.setattr(
        release,
        "verify_artifacts",
        lambda dist_dir, expected_version: (dist_dir / "wheel", dist_dir / "sdist"),
    )
    monkeypatch.setattr(release, "venv_python", lambda venv: venv / "bin" / "python")

    release.run_release_checks(root, "3.0.1")

    assert not expected_config.exists()
    assert not expected_site_dir.exists()
    assert root.joinpath("docs", "keep.txt").exists()


def test_check_github_alerts_rejects_open_alerts(tmp_path, monkeypatch):
    monkeypatch.setattr(
        release.subprocess, "check_output", lambda *args, **kwargs: "2\n1\n"
    )

    with pytest.raises(RuntimeError, match="3 open Dependabot alerts"):
        release.check_github_alerts(tmp_path)
