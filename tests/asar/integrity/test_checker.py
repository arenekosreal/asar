"""Test ./src/asar/integrity/checker.py functions."""

import pytest
from asar.integrity.checker import IntegrityChecker


def test_checker():
    """Check if IntegrityChecker is not implemented."""
    with pytest.raises(TypeError):
        _ = IntegrityChecker()  # type: ignore
