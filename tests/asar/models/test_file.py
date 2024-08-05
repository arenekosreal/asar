"""Test ./src/asar/models/file.py functions."""

from asar.models.file import FileMetaDictInfo
from asar.models.file import to_file_meta_info as _to_file_meta_info


def test_to_file_meta_info():
    """Test to_file_meta_info function."""
    size = 42
    json: FileMetaDictInfo = {
        "size": size,
        "offset": "0",
        "integrity": {
            "algorithm": "SHA256",
            "hash": "1233211234567",
            "blockSize": 4096,
            "blocks": ["1233211234567"],
        },
    }
    meta = _to_file_meta_info(json)
    assert meta.integrity is not None
    assert meta.offset == "0"
    assert meta.size == size
    assert meta.to_json() == json
