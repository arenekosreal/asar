import math
import json
import sys
import logging
from pathlib import PurePath
from typing import Callable, Literal
from enum import Enum
from asar.integrity.checker import IntegrityChecker
from asar.integrity.sha256 import Sha256Checker
from asar.models.file import FileMetaInfo
from asar.models.folder import (
    FolderMetaInfo,
    FolderMetaDictInfo,
    to_folder_meta_info as _to_folder_meta_info,
)
from asar.models.integrity import AlgorithmType


__version__ = "0.1.0"

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_sh = logging.StreamHandler()
_sh.setLevel(_logger.level)
_fmt = logging.Formatter("%(asctime)s-%(levelname)s-%(message)s", "%Y-%m-%d %H:%M:%S")
_sh.setFormatter(_fmt)
[_logger.removeHandler(handler) for handler in _logger.handlers]
_logger.addHandler(_sh)


class Alignment(Enum):
    """How many bytes are the asar archive is aligned in."""

    DWORD = 4


class ChecksumMismatchError(Exception): ...


class Asar:
    """An asar archive
    See also: https://knifecoat.com/Posts/ASAR+Format+Spec
    """

    HEAD_MAGIC_SIZE = 4
    HEAD_MAGIC_VALUE = 4
    HEAD_JSON_HEADER_SIZE_SIZE = 4  # Size of header size
    HEAD_JSON_HEADER_SIZE_SIZE_SIZE = 4  # Size of `Size of header size`
    HEAD_JSON_HEADER_SIZE_SIZE_SIZE_SIZE = 4  # Size of `Size of `Size of header size``
    HEAD_SIZE = (
        HEAD_MAGIC_SIZE
        + HEAD_JSON_HEADER_SIZE_SIZE_SIZE_SIZE
        + HEAD_JSON_HEADER_SIZE_SIZE_SIZE
        + HEAD_JSON_HEADER_SIZE_SIZE
    )

    def __init__(self, raw: bytes, alignment: Alignment = Alignment.DWORD):
        """Initialize Asar instance with arguments given.

        Args:
            raw(bytes): The content of asar archive.
            alignment(Alignment): How the archive is aligned, defaults to Alignment.DWORD
        """
        try:
            assert (
                int.from_bytes(raw[0 : self.HEAD_MAGIC_SIZE], sys.byteorder)
                == self.HEAD_MAGIC_VALUE
            )
        except AssertionError as e:
            raise ValueError("Invalid magic number") from e
        self.alignment = alignment
        self._raw = raw
        json_header_size_start = (
            self.HEAD_MAGIC_SIZE
            + self.HEAD_JSON_HEADER_SIZE_SIZE_SIZE
            + self.HEAD_JSON_HEADER_SIZE_SIZE_SIZE_SIZE
        )
        json_header_size_end = self.HEAD_SIZE
        json_header_size = raw[json_header_size_start:json_header_size_end]
        json_header_size = int.from_bytes(json_header_size, sys.byteorder)
        _logger.debug("JSON header size is %s", json_header_size)
        json_header_start = self.HEAD_SIZE
        json_header_end = json_header_start + json_header_size
        self.json_header: dict[Literal["files"], FolderMetaDictInfo] = json.loads(
            raw[json_header_start:json_header_end]
        )
        self.meta = _to_folder_meta_info(self.json_header["files"])
        self._content_start = (
            math.ceil(json_header_end / self.alignment.value) * self.alignment.value
        )

    def __bytes__(self) -> bytes:
        head_magic = self.HEAD_MAGIC_VALUE.to_bytes(self.HEAD_MAGIC_SIZE, sys.byteorder)
        json_header_data = json.dumps(
            {"files": self.meta.to_json()}, sort_keys=True
        ).encode()
        json_header_size = len(json_header_data).to_bytes(
            self.HEAD_JSON_HEADER_SIZE_SIZE,
            sys.byteorder,
        )
        json_header_size_size = (
            len(json_header_data) + len(json_header_size)
        ).to_bytes(self.HEAD_JSON_HEADER_SIZE_SIZE_SIZE, sys.byteorder)
        json_header_size_size_size = (
            len(json_header_data) + len(json_header_size) + len(json_header_size_size)
        ).to_bytes(self.HEAD_JSON_HEADER_SIZE_SIZE_SIZE_SIZE, sys.byteorder)
        file_header = (
            head_magic
            + json_header_size_size_size
            + json_header_size_size
            + json_header_size
        )
        assert len(file_header) == self.HEAD_SIZE
        archive_header = file_header + json_header_data
        padding = math.ceil(
            len(archive_header) / self.alignment.value
        ) * self.alignment.value - len(archive_header)
        archive_header += bytes(padding)
        return archive_header + self.content

    @property
    def content(self) -> bytes:
        """The content of all files in the archive."""
        return self._raw[self._content_start :]

    @property
    def _checkers(self) -> dict[AlgorithmType, IntegrityChecker]:
        return {"SHA256": Sha256Checker()}

    def get_file(
        self,
        info: FileMetaInfo,
        strict: bool = True,
        transform: Callable[[bytes], bytes] | None = None,
    ) -> bytes:
        """Get the file in archive by FileMetaInfo given.

        Args:
            info(FileMetaInfo): The metainfo of target file.
            strict(bool): If ensure checksum is valid.
            transform(Callable[[bytes], bytes] | None): apply to the bytes and return its result instead raw result. Defaults to None

        Returns:
            bytes: The content of file.

        Raises:
            ValueError: If this file is unpacked.
            IndexError: If the offset is out of range.
            ChecksumMismatchError: If strict is True and failed to check integrity
        """
        if info.offset is None:
            raise ValueError("This file is unpacked.")
        offset = int(info.offset)
        if offset > len(self.content) or offset < 0:
            raise IndexError("Cannot find file at offset %s", offset)
        content = self.content[offset : offset + info.size]
        if info.integrity is not None:
            if not self._checkers[info.integrity.algorithm].check(
                content, info.integrity
            ):
                if strict:
                    raise ChecksumMismatchError()
                _logger.warning("Checksum of file is not match meta data!")
            else:
                _logger.info("Check integrity successful!")
        else:
            _logger.warning("There is no integrity info for the file.")
        if transform is not None:
            return transform(content)
        return content

    def at(self, path: PurePath) -> FolderMetaInfo | FileMetaInfo:
        """Get metainfo at path.

        Args:
            path(PurePath): An absolute path relative to the root directory in archive.

        Returns:
            FolderMetaInfo | FileMetaInfo: The metainfo at path given.

        Raises:
            FileNotFoundError: If no such file or directory.
        """
        path = path.relative_to("/")
        if path == PurePath("/"):
            return self.meta
        for current_path, folders, files in self.meta.walk():
            for name, meta in folders.items():
                if current_path / name == path:
                    return meta
            for name, meta in files.items():
                if current_path / name == path:
                    return meta
        raise FileNotFoundError("No such file or directory", path)


__all__ = ["__version__", "Alignment", "ChecksumMismatchError", "Asar"]
