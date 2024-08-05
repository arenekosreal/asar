"""Test ./src/asar/cli/list.py functions."""

from pathlib import Path
from asar.cli.list import list_archive as _list_archive


def test_list_archive(asar_path: Path):
    """Test list_archive function."""
    _list_archive(asar_path, False)
    _list_archive(asar_path, True)
