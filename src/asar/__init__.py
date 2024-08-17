"""Operate asar archive in a convient way without nodejs installed."""

__version__ = "0.2.0"

import sys
import json
import math
import logging
from enum import Enum
from typing import Literal
from typing import TypeGuard
from typing import OrderedDict
from typing import overload
from typing import override
from pathlib import Path
from pathlib import PurePath
from itertools import chain
from asar.file.base import AsarFile
from asar.file.base import FileMetaInfo
from asar.file.base import FileMetaDictInfo


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_sh = logging.StreamHandler()
_sh.setLevel(_logger.level)
_fmt = logging.Formatter("%(asctime)s-%(levelname)s-%(message)s", "%Y-%m-%d %H:%M:%S")
_sh.setFormatter(_fmt)
[_logger.removeHandler(handler) for handler in _logger.handlers]
_logger.addHandler(_sh)


def _is_debug() -> bool:
    return _logger.level == logging.DEBUG


FolderMetaDictInfo = dict[
    Literal["files"],
    dict[str, "FileMetaDictInfo | FolderMetaDictInfo"],
]


class Alignment(Enum):
    """How many bytes are the asar archive is aligned in."""

    DWORD = 4


class Asar(dict[PurePath, AsarFile]):
    """An asar archive.

    You can use it like dict[PurePath, AsarFile] to access files in the archive.

    See Also:
        https://knifecoat.com/Posts/ASAR+Format+Spec
        https://github.com/electron/asar#format
    """

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, *, alignment: Alignment) -> None: ...

    @overload
    def __init__(self, raw: bytes) -> None: ...

    @overload
    def __init__(self, raw: bytes, alignment: Alignment) -> None: ...

    def __init__(
        self,
        raw: bytes | None = None,
        alignment: Alignment = Alignment.DWORD,
    ):
        """Initialize an Asar archive with arguments given.

        Args:
            raw(bytes): The content of asar archive.
            alignment(Alignment): How the archive is aligned.
        """
        super().__init__()
        self.alignment = alignment
        if raw is None:
            _logger.debug("Creating an empty archive.")
        else:
            _logger.debug("Parsing input bytes...")
            magic_header = raw[: self.alignment.value]
            if magic_header != self.archive_magic_bytes:
                raise ValueError("Invalid file magic header.")
            json_header_size_start = self.alignment.value * 3
            json_header_size_end = self.alignment.value * 4
            json_header_size = raw[json_header_size_start:json_header_size_end]
            json_header_size = int.from_bytes(json_header_size, sys.byteorder)
            json_header_start = json_header_size_end
            json_header_end = json_header_start + json_header_size
            json_header_bytes = raw[json_header_start:json_header_end]
            if _is_debug():
                _ = Path("headers.debug.json").write_text(
                    json.dumps(json_header_bytes, indent=4),
                    encoding="utf-8",
                )
            json_header: FolderMetaDictInfo = json.loads(json_header_bytes)
            padding = self._get_padding_size(json_header_bytes)
            self._flattern_json_header_recursively(
                raw[json_header_end + padding :],
                json_header,
            )

    @property
    def archive_magic_bytes(self) -> bytes:
        """Magic number bytes of archive."""
        return self.alignment.value.to_bytes(self.alignment.value, sys.byteorder)

    @property
    def json_header(self) -> FolderMetaDictInfo:
        """Get json header of archive."""
        return self._build_json_header_recursively()

    @property
    def folders(self) -> list[PurePath]:
        """Get folders' paths."""
        folders = chain.from_iterable(f.parents for f in self.files)
        folders = list(set(folders))
        if PurePath() in folders:
            folders.remove(PurePath())
        return sorted(folders)

    @property
    def files(self) -> list[PurePath]:
        """Get files' paths."""
        return sorted(self.keys())

    def __bytes__(self) -> bytes:
        """Convert Asar object to valid bytes."""
        self._sync_meta_info()
        content = bytes().join(self[f].content for f in self.files)
        json_header = json.dumps(self.json_header, separators=(",", ":")).encode()
        json_header_size = len(json_header).to_bytes(
            self.alignment.value,
            sys.byteorder,
        )
        padding = self._get_padding_size(json_header)
        padding = bytes(padding)
        prefix = json_header_size + json_header + padding
        prefix = self._pickle(prefix)
        prefix = self._pickle(prefix)
        header = self.archive_magic_bytes + prefix
        if (len(header) % self.alignment.value) != 0:
            raise RuntimeError("Failed to align header part")
        return header + content

    @override
    def __setitem__(self, key: PurePath, value: AsarFile, /) -> None:
        if key.is_absolute():
            key = key.relative_to("/")
        return super().__setitem__(key, value)

    @override
    def __getitem__(self, key: PurePath, /) -> AsarFile:
        if key.is_absolute():
            key = key.relative_to("/")
        return super().__getitem__(key)

    def _get_padding_size(self, data: bytes) -> int:
        size = len(data)
        block_count = math.ceil(size / self.alignment.value)
        aligned_size = block_count * self.alignment.value
        return aligned_size - size

    def _pickle(self, data: bytes) -> bytes:
        size = len(data)
        size = size.to_bytes(self.alignment.value, sys.byteorder)
        return size + data

    def _unpickle(self, data: bytes) -> tuple[int, bytes]:
        size = data[: self.alignment.value]
        size = int.from_bytes(size, sys.byteorder)
        return size, data[self.alignment.value :]

    def _flattern_json_header_recursively(
        self,
        content: bytes,
        data: FolderMetaDictInfo,
        parent: PurePath | None = None,
    ):
        def _is_folder_meta_dict_info(
            meta: FileMetaDictInfo | FolderMetaDictInfo,
        ) -> TypeGuard[FolderMetaDictInfo]:
            return list(meta.keys()) == ["files"]

        def _is_file_meta_dict_info(
            meta: FileMetaDictInfo | FolderMetaDictInfo,
        ) -> TypeGuard[FileMetaDictInfo]:
            return "files" not in meta

        if parent is None:
            parent = PurePath()
        for name, meta in data["files"].items():
            if _is_folder_meta_dict_info(meta):
                self._flattern_json_header_recursively(content, meta, parent / name)
            elif _is_file_meta_dict_info(meta):
                typed_meta = FileMetaInfo.from_json(meta)
                offset = typed_meta.offset
                if offset is None:
                    raise RuntimeError("This file is unpacked.")
                offset = int(offset)
                content_start = offset
                content_end = offset + typed_meta.size
                self[parent / name] = AsarFile(
                    typed_meta,
                    content[content_start:content_end],
                )
            else:
                raise NotImplementedError("This meta info is not supported.")

    def _build_json_header_recursively(
        self,
        parent: PurePath | None = None,
    ) -> FolderMetaDictInfo:
        if parent is None:
            parent = PurePath()

        def _is_direct_child_of_parent(i: PurePath) -> bool:
            return i.is_relative_to(parent) and len(i.relative_to(parent).parts) == 1

        filtered = filter(_is_direct_child_of_parent, self.files + self.folders)

        header: FolderMetaDictInfo = {"files": OrderedDict()}
        # TODO
        for path in sorted(filtered):
            if path in self.files:
                meta = self[path].meta
                header["files"][path.name] = meta.to_json()
            else:
                header["files"][path.name] = self._build_json_header_recursively(path)
        return header

    def _sync_meta_info(self):
        offset = 0
        for f in self.files:
            if self[f].meta.offset is not None:
                size = len(self[f].content)
                self[f].meta.offset = str(offset)
                offset += size


__all__ = ["Alignment", "Asar", "__version__"]
