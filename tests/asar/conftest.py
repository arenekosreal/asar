"""Fixtures for tests."""

import os
import sys
import pytest
import shutil
import subprocess
from pathlib import Path


@pytest.fixture
def asar_path(tmp_path: Path) -> Path:
    """Generate a random asar archive and returns its path."""
    path = os.environ["PATH"].split(os.pathsep)
    if sys.prefix != sys.base_prefix:
        venv_path_gen = (i for i in path if i.startswith(sys.prefix))
        venv_path = next(venv_path_gen, None)
        while venv_path is not None:
            path.remove(venv_path)
            venv_path = next(venv_path_gen, None)
    path_without_venv = os.pathsep.join(path)
    asar = shutil.which("asar", path=path_without_venv)

    if asar is None:
        raise RuntimeError("@electron/asar is not installed.")

    test_archive = tmp_path / "test"
    test_archive.mkdir(exist_ok=True)
    files = test_archive / "test.bin"
    _ = files.write_bytes(os.urandom(42))
    _ = subprocess.check_call(
        [asar, "pack", str(test_archive), str(test_archive) + ".asar"],
    )
    return Path(str(test_archive) + ".asar")
