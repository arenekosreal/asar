"""Test ./src/asar/base.py functions."""

import pytest
from asar.base import MetaInfo


def test_base():
    """Check if MetaInfo is not implemented."""
    with pytest.raises(TypeError):
        _ = MetaInfo()  # type:ignore
