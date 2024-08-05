"""Test ./src/asar/models/folder.py functions."""

from pathlib import PurePath
from asar.models.folder import FolderMetaDictInfo
from asar.models.folder import to_folder_meta_info as _to_folder_meta_info


def test_to_folder_meta_info():
    """Test to_folder_meta_info function."""
    size = 42
    json: FolderMetaDictInfo = {
        "example.bin": {
            "size": size,
            "offset": "0",
            "integrity": {
                "algorithm": "SHA256",
                "hash": "1233211234567",
                "blockSize": 4096,
                "blocks": ["1233211234567"],
            },
        },
    }
    meta = _to_folder_meta_info(json)
    assert len(meta.files) == 1
    assert list(meta.files.keys()) == ["example.bin"]
    for path, folders, files in meta.walk():
        assert path == PurePath("./")
        assert len(folders) == 0
        assert len(files) == 1
