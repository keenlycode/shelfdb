"""Release validation for ShelfDB."""

from __future__ import annotations

import subprocess
import tarfile
import tempfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

PIP_AUDIT_VERSION = "2.10.1"
TWINE_VERSION = "7.0.0"
SUPPORTED_PYTHONS = ("3.12", "3.13")
DEPENDABOT_ALERTS_ENDPOINT = (
    "repos/keenlycode/shelfdb/dependabot/alerts?state=open&per_page=100"
)


def run_command(command: list[str], *, cwd: Path) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def metadata_version(content: bytes) -> tuple[str, str]:
    metadata = BytesParser().parsebytes(content)
    return str(metadata["Name"]), str(metadata["Version"])


def verify_artifacts(dist_dir: Path, expected_version: str) -> tuple[Path, Path]:
    wheels = sorted(dist_dir.glob("shelfdb-*.whl"))
    sdists = sorted(dist_dir.glob("shelfdb-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError(
            "Expected exactly one ShelfDB wheel and one source distribution"
        )

    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        metadata_paths = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_paths) != 1:
            raise RuntimeError("Expected exactly one wheel METADATA file")
        wheel_name, wheel_version = metadata_version(archive.read(metadata_paths[0]))

    sdist = sdists[0]
    with tarfile.open(sdist, "r:gz") as archive:
        metadata_members = [
            member
            for member in archive.getmembers()
            if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
        ]
        if len(metadata_members) != 1:
            raise RuntimeError("Expected exactly one source distribution PKG-INFO file")
        extracted = archive.extractfile(metadata_members[0])
        if extracted is None:
            raise RuntimeError("Could not read source distribution metadata")
        sdist_name, sdist_version = metadata_version(extracted.read())

    expected = ("shelfdb", expected_version)
    if (wheel_name, wheel_version) != expected:
        raise RuntimeError(
            f"Wheel metadata is {(wheel_name, wheel_version)!r}; expected {expected!r}"
        )
    if (sdist_name, sdist_version) != expected:
        raise RuntimeError(
            f"Source metadata is {(sdist_name, sdist_version)!r}; expected {expected!r}"
        )

    print(f"Verified ShelfDB {expected_version} artifact metadata")
    return wheel, sdist


def venv_python(venv: Path) -> Path:
    windows_python = venv / "Scripts" / "python.exe"
    return windows_python if windows_python.exists() else venv / "bin" / "python"


def check_github_alerts(root: Path) -> None:
    command = [
        "gh",
        "api",
        "--paginate",
        DEPENDABOT_ALERTS_ENDPOINT,
        "--jq",
        "length",
    ]
    print("+", " ".join(command), flush=True)
    output = subprocess.check_output(command, cwd=root, text=True)
    count = sum(int(line) for line in output.splitlines() if line.strip())
    print(f"Open Dependabot alerts: {count}")
    if count:
        raise RuntimeError(f"Found {count} open Dependabot alerts")


def run_release_checks(
    root: Path, expected_version: str, *, check_github: bool = False
) -> None:
    """Run the complete, non-publishing release gate."""
    with tempfile.TemporaryDirectory(prefix="shelfdb-release-check-") as tmp:
        work = Path(tmp)
        requirements = work / "requirements.txt"
        site_dir = work / "site"
        dist_dir = work / "dist"
        smoke_venv = work / "smoke-venv"

        run_command(["uv", "lock", "--check"], cwd=root)
        run_command(
            [
                "uv",
                "export",
                "--quiet",
                "--frozen",
                "--all-groups",
                "--no-emit-project",
                "--format",
                "requirements.txt",
                "--output-file",
                str(requirements),
            ],
            cwd=root,
        )
        run_command(
            [
                "uvx",
                f"pip-audit=={PIP_AUDIT_VERSION}",
                "--strict",
                "--progress-spinner",
                "off",
                "--requirement",
                str(requirements),
            ],
            cwd=root,
        )
        if check_github:
            check_github_alerts(root)
        run_command(
            ["uv", "run", "--frozen", "ruff", "format", "--check", "."],
            cwd=root,
        )
        run_command(["uv", "run", "--frozen", "ruff", "check", "."], cwd=root)
        run_command(["uv", "run", "--frozen", "ty", "check"], cwd=root)
        for python_version in SUPPORTED_PYTHONS:
            run_command(
                [
                    "uv",
                    "run",
                    "--isolated",
                    "--frozen",
                    "--python",
                    python_version,
                    "pytest",
                    "-q",
                ],
                cwd=root,
            )
        run_command(
            [
                "uv",
                "run",
                "--frozen",
                "mkdocs",
                "build",
                "--strict",
                "--site-dir",
                str(site_dir),
            ],
            cwd=root,
        )
        run_command(["uv", "build", "--out-dir", str(dist_dir)], cwd=root)
        wheel, sdist = verify_artifacts(dist_dir, expected_version)
        run_command(
            [
                "uvx",
                f"twine=={TWINE_VERSION}",
                "check",
                str(wheel),
                str(sdist),
            ],
            cwd=root,
        )

        run_command(
            ["uv", "venv", "--python", SUPPORTED_PYTHONS[0], str(smoke_venv)],
            cwd=root,
        )
        python = venv_python(smoke_venv)
        run_command(
            ["uv", "pip", "install", "--python", str(python), str(wheel)],
            cwd=work,
        )
        run_command(
            [
                str(python),
                "-I",
                "-c",
                "import shelfdb; from shelfdb.client import Client; from shelfdb.shelf import DB",
            ],
            cwd=work,
        )

    print(f"ShelfDB {expected_version} release check passed")
