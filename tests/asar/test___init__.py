"""Test ./src/asar/__init__.py functions."""

from asar import Asar
from pathlib import Path


def test___bytes__(asar_path: Path):
    """Test Asar.__bytes__ function."""
    content = asar_path.read_bytes()
    asar = Asar(content)
    assert (bytes(asar)[:16]) == content[:16]
