"""Fixtures for tests."""

import os
import pytest
import random
import hashlib
from typing import OrderedDict
from asar.integrity.base import IntegrityInfo
from asar.integrity.base import IntegrityDictInfo


@pytest.fixture
def random_meta_valid_dict_info() -> IntegrityDictInfo:
    """Get a random valid IntegrityDictInfo object."""
    size = 42
    block_size = 4096
    hash_ = hashlib.sha256(os.urandom(size)).hexdigest()
    integrity: IntegrityDictInfo = OrderedDict()
    integrity["algorithm"] = "SHA256"
    integrity["hash"] = hash_
    integrity["blockSize"] = block_size
    integrity["blocks"] = [hash_]
    return integrity


@pytest.fixture
def random_meta_invalid_dict_info(
    random_meta_valid_dict_info: IntegrityDictInfo,
) -> IntegrityDictInfo:
    """Get a random invalid IntegrityDictInfo object."""
    keys = list(random_meta_valid_dict_info)
    key = random.choice(keys)
    del random_meta_valid_dict_info[key]
    return random_meta_valid_dict_info


@pytest.fixture
def random_meta_type_invalid_dict_info(
    random_meta_valid_dict_info: IntegrityDictInfo,
) -> IntegrityDictInfo:
    """Get a random invalid type IntegrityDictInfo object."""
    keys = list(random_meta_valid_dict_info)
    key = random.choice(keys)
    left_keys = keys.copy()
    left_keys.remove(key)
    value = random_meta_valid_dict_info[random.choice(left_keys)]
    random_meta_valid_dict_info[key] = value
    return random_meta_valid_dict_info


@pytest.fixture
def random_meta_algorithm_invalid_dict_info(
    random_meta_valid_dict_info: IntegrityDictInfo,
) -> IntegrityDictInfo:
    """Get a random invalid algorithm IngegrityDictInfo object."""
    random_meta_valid_dict_info["algorithm"] = "Unknown"
    return random_meta_valid_dict_info


@pytest.fixture
def random_meta_info(random_meta_valid_dict_info: IntegrityDictInfo) -> IntegrityInfo:
    """Get a random IntegrityInfo instance."""
    return IntegrityInfo.from_json(random_meta_valid_dict_info)
