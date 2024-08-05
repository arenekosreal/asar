"""Test ./src/asar/models/integrity.py functions."""

from asar.models.integrity import IntegrityDictInfo
from asar.models.integrity import to_integrity_info as _to_integrity_info


def test_to_integrity_info():
    """Test to_integrity_info function."""
    block_size = 4096
    json: IntegrityDictInfo = {
        "algorithm": "SHA256",
        "hash": "1233211234567",
        "blockSize": block_size,
        "blocks": ["1233211234567"],
    }
    meta = _to_integrity_info(json)
    assert meta.algorithm == "SHA256"
    assert meta.hash_ == "1233211234567"
    assert meta.blocksize == block_size
    assert meta.blocks == ["1233211234567"]
