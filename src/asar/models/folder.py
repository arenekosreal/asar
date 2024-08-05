"""Data class to store folder info in json header."""

import logging
from typing import Literal
from typing import Generator
from typing import TypeGuard
from typing import override
from pathlib import PurePath
from dataclasses import dataclass
from asar.models.file import FileMetaInfo
from asar.models.file import FileMetaDictInfo
from asar.models.file import to_file_meta_info as _to_file_meta_info
from asar.models.metainfo import MetaInfo


_logger = logging.getLogger(__name__)

_WalkReturnType = tuple[PurePath, dict[str, "FolderMetaInfo"], dict[str, FileMetaInfo]]

FolderMetaDictInfo = dict[
    str,
    FileMetaDictInfo | dict[Literal["files"], "FolderMetaDictInfo"],
]


@dataclass
class FolderMetaInfo(MetaInfo):
    """The basic model of folder in meta info.

    ```json
    {
        "<folder name>": {
            "files": <FileMetaDictInfo> | <FolderMetaDictInfo>
        },
        "<file name>": <FileMetaDictInfo>
    }
    ```
    """

    files: dict[str, "FileMetaInfo | FolderMetaInfo"]

    @override
    def to_json(self) -> FolderMetaDictInfo:
        base: FolderMetaDictInfo = {}
        for name, meta in self.files.items():
            if isinstance(meta, FileMetaInfo):
                base[name] = meta.to_json()
            else:
                base[name] = {"files": meta.to_json()}
        return base

    @property
    def _folders(self) -> "filter[tuple[str, FolderMetaInfo]]":
        def _filter_folder(
            i: tuple[str, "FileMetaInfo | FolderMetaInfo"],
        ) -> TypeGuard[tuple[str, "FolderMetaInfo"]]:
            return isinstance(i[1], FolderMetaInfo)

        return filter(_filter_folder, self.files.items())

    @property
    def _files(self) -> "filter[tuple[str, FileMetaInfo]]":
        def _filter_file(
            i: tuple[str, "FileMetaInfo | FolderMetaInfo"],
        ) -> TypeGuard[tuple[str, FileMetaInfo]]:
            return isinstance(i[1], FileMetaInfo)

        return filter(_filter_file, self.files.items())

    def walk(
        self,
        prefix: PurePath | None = None,
    ) -> Generator[_WalkReturnType, None, None]:
        """Walk sub-directories and files like `os.walk`."""
        if prefix is None:
            prefix = PurePath("./")
        yield prefix, dict(self._folders), dict(self._files)

        for name, meta in self._folders:
            yield from meta.walk(prefix / name)


def to_folder_meta_info(json: FolderMetaDictInfo) -> FolderMetaInfo:
    """Generate FolderMetaInfo from FolderMetaDictInfo."""
    files: dict[str, FileMetaInfo | FolderMetaInfo] = {}
    for name, item in json.items():
        if list(item.keys()) == ["files"]:
            _logger.debug("Creating folder meta info for %s", name)
            files[name] = to_folder_meta_info(item["files"])  # pyright: ignore
        else:
            _logger.debug("Creating file meta info for %s", name)
            files[name] = _to_file_meta_info(item)  # pyright: ignore
    return FolderMetaInfo(files)
