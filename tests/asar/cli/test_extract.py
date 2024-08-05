"""Test ./src/asar/cli/extract.py functions."""

import os
from pathlib import Path
from pathlib import PurePath
from asar.cli.extract import extract as _extract
from asar.cli.extract import extract_file as _extract_file


def test_extract_file(asar_path: Path):
    """Test extract_file function."""
    os.chdir(asar_path.parent)
    _extract_file(asar_path, PurePath("/test.bin"))
    target = Path.cwd() / "test.bin"
    assert target.exists()


def test_extract(asar_path: Path):
    """Test extract function."""
    os.chdir(asar_path.parent)
    dest = Path.cwd() / "test_extracted"
    _extract(asar_path, dest)
    assert dest.is_dir()
    assert (dest / "test.bin").exists()
