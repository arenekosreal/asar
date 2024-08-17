"""Test ./src/asar/integrity/sha256.py functions."""

import os
import hashlib
from asar.integrity.base import IntegrityInfo
from asar.integrity.sha256 import Sha256Checker


def test_check():
    """Test check function."""
    checker = Sha256Checker()
    content = os.urandom(42)
    sha256 = hashlib.sha256(content).hexdigest()
    integrity = IntegrityInfo("SHA256", sha256, 4096, [sha256])
    assert checker.check(content, integrity)
