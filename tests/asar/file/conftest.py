"""Fixtures for tests."""

import os
import pytest
import random
import hashlib
from typing import Literal
from typing import OrderedDict
from asar.file.base import AsarFile
from asar.file.base import FileMetaInfo
from asar.file.base import FileMetaDictInfo
from asar.integrity.base import IntegrityDictInfo


@pytest.fixture
def random_valid_asar_file() -> AsarFile:
    """Get a random valid AsarFile instance."""
    max_offset = 65535
    max_size = 65535
    block_size = 42

    size = random.randint(0, max_size)
    content = os.urandom(size)
    sha256 = hashlib.sha256(content).hexdigest()

    info: FileMetaDictInfo = OrderedDict()
    info["offset"] = str(random.randint(0, max_offset))
    info["size"] = size
    integrity: IntegrityDictInfo = OrderedDict()
    integrity["algorithm"] = "SHA256"
    integrity["hash"] = sha256
    integrity["blockSize"] = block_size
    integrity["blocks"] = []
    for part in [
        content[i : i + block_size] for i in range(0, len(content), block_size)
    ]:
        integrity["blocks"].append(hashlib.sha256(part).hexdigest())
    info["integrity"] = integrity
    return AsarFile(FileMetaInfo.from_json(info), content)


@pytest.fixture
def random_invalid_asar_file(random_valid_asar_file: AsarFile) -> AsarFile:
    """Get a random invalid AsarFile instance."""
    random_valid_asar_file.content = bytes()
    return random_valid_asar_file


@pytest.fixture
def random_meta_valid_dict_info(random_valid_asar_file: AsarFile) -> FileMetaDictInfo:
    """Get a random valid FileMetaDictInfo object."""
    return random_valid_asar_file.meta.to_json()


@pytest.fixture
def random_meta_invalid_dict_info(
    random_meta_valid_dict_info: FileMetaDictInfo,
) -> FileMetaDictInfo:
    """Get a random invalid FileMetaDictInfo object."""
    key: Literal["size", "integrity"] = random.choice(["size", "integrity"])
    del random_meta_valid_dict_info[key]
    return random_meta_valid_dict_info


@pytest.fixture
def random_meta_invalid_type_dict_info(
    random_meta_valid_dict_info: FileMetaDictInfo,
) -> FileMetaDictInfo:
    """Get a random invalid type FileMetaDictInfo object."""
    keys = list(random_meta_valid_dict_info)
    key = random.choice(keys)
    left_keys = keys.copy()
    left_keys.remove(key)
    value = random_meta_valid_dict_info[random.choice(left_keys)]
    random_meta_valid_dict_info[key] = value
    return random_meta_valid_dict_info


@pytest.fixture
def random_meta_info(random_meta_valid_dict_info: FileMetaDictInfo) -> FileMetaInfo:
    """Get a random FileMetaInfo instance."""
    return FileMetaInfo.from_json(random_meta_valid_dict_info)
