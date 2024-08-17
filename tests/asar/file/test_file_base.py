"""Test ./src/asar/file/base.py functions."""

import pytest
from asar.file.base import AsarFile
from asar.file.base import FileMetaInfo
from asar.file.base import FileMetaDictInfo


class TestFileMetaInfo:
    """Test FileMetaInfo class function."""

    def test_from_json_valid(self, random_meta_valid_dict_info: FileMetaDictInfo):
        """Test FileMetaInfo.from_json function."""
        meta = FileMetaInfo.from_json(random_meta_valid_dict_info)
        assert meta.executable == random_meta_valid_dict_info.get("executable", False)
        assert meta.offset == random_meta_valid_dict_info.get("offset")
        assert meta.size == random_meta_valid_dict_info["size"]
        assert meta.unpacked == random_meta_valid_dict_info.get("unpacked", False)

    def test_from_json_invalid(self, random_meta_invalid_dict_info: FileMetaDictInfo):
        """Test FileMetaInfo.from_json function."""
        with pytest.raises(ValueError, match="No"):
            _ = FileMetaInfo.from_json(random_meta_invalid_dict_info)

    def test_from_json_invalid_type(
        self,
        random_meta_invalid_type_dict_info: FileMetaDictInfo,
    ):
        """Test FileMetaInfo.from_json function."""
        with pytest.raises(ValueError, match="Invalid"):
            _ = FileMetaInfo.from_json(random_meta_invalid_type_dict_info)

    def test_to_json(self, random_meta_info: FileMetaInfo):
        """Test FileMetaInfo.to_json function."""
        meta = random_meta_info.to_json()
        assert meta.get("executable", False) == random_meta_info.executable
        assert meta.get("offset") == random_meta_info.offset
        assert meta["size"] == random_meta_info.size
        assert meta.get("unpacked", False) == random_meta_info.unpacked


class TestAsarFile:
    """Test AsarFile class function."""

    def test_check_invalid(self, random_invalid_asar_file: AsarFile):
        """Test AsarFile.check function."""
        assert not random_invalid_asar_file.check()

    def test_check_valid(self, random_valid_asar_file: AsarFile):
        """Test AsarFile.check function."""
        assert random_valid_asar_file.check()
