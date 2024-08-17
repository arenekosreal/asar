"""Test ./src/asar/integrity/base.py functions."""

import pytest
from asar.integrity.base import IntegrityInfo
from asar.integrity.base import IntegrityDictInfo


def test_from_json_valid(random_meta_valid_dict_info: IntegrityDictInfo):
    """Test IntegrityInfo.from_json function."""
    meta = IntegrityInfo.from_json(random_meta_valid_dict_info)
    assert meta.algorithm == random_meta_valid_dict_info["algorithm"]
    assert meta.blocks == random_meta_valid_dict_info["blocks"]
    assert meta.blocksize == random_meta_valid_dict_info["blockSize"]
    assert meta.hash_ == random_meta_valid_dict_info["hash"]


def test_from_json_invalid(random_meta_invalid_dict_info: IntegrityDictInfo):
    """Test IntegrityInfo.from_json function."""
    with pytest.raises(ValueError, match="No"):
        _ = IntegrityInfo.from_json(random_meta_invalid_dict_info)


def test_from_json_invalid_type(random_meta_type_invalid_dict_info: IntegrityDictInfo):
    """Test IntegrityInfo.from_json function."""
    with pytest.raises(ValueError, match="Invalid"):
        _ = IntegrityInfo.from_json(random_meta_type_invalid_dict_info)


def test_from_json_invalid_algorithm(
    random_meta_algorithm_invalid_dict_info: IntegrityDictInfo,
):
    """Test IntegrityInfo.from_json function."""
    with pytest.raises(NotImplementedError):
        _ = IntegrityInfo.from_json(random_meta_algorithm_invalid_dict_info)


def test_to_json(random_meta_info: IntegrityInfo):
    """Test IntegrityInfo.to_json function."""
    meta = random_meta_info.to_json()
    assert meta["algorithm"] == random_meta_info.algorithm
    assert meta["hash"] == random_meta_info.hash_
    assert meta["blockSize"] == random_meta_info.blocksize
    assert meta["blocks"] == random_meta_info.blocks
