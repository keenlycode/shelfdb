import importlib.util
import io
import sys
import tarfile
import zipfile
from pathlib import Path

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


def test_verify_artifacts_returns_valid_wheel(tmp_path):
    expected_artifacts = write_artifacts(tmp_path)

    artifacts = release.verify_artifacts(tmp_path, "3.0.1")

    assert artifacts == expected_artifacts


def test_verify_artifacts_rejects_wrong_version(tmp_path):
    write_artifacts(tmp_path, version="3.0.0")

    with pytest.raises(RuntimeError, match="expected"):
        release.verify_artifacts(tmp_path, "3.0.1")
