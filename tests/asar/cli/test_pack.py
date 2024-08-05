"""Test ./src/asar/cli/pack.py functions."""

import pytest
from pathlib import Path
from asar.cli.pack import pack as _pack


def test_pack(tmp_path: Path):
    """Test pack function."""
    with pytest.raises(NotImplementedError):
        _pack(tmp_path / "test", tmp_path / "test.asar", None, None, None, False)
