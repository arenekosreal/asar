import logging
from dataclasses import dataclass
from pathlib import PurePath
from typing import Generator, Literal, override, TypeGuard
from asar.models.file import (
    FileMetaInfo,
    FileMetaDictInfo,
    to_file_meta_info as _to_file_meta_info,
)
from asar.models.metainfo import MetaInfo


_logger = logging.getLogger(__name__)

_WalkReturnType = tuple[PurePath, dict[str, "FolderMetaInfo"], dict[str, FileMetaInfo]]

FolderMetaDictInfo = dict[
    str, FileMetaDictInfo | dict[Literal["files"], "FolderMetaDictInfo"]
]


@dataclass
class FolderMetaInfo(MetaInfo):
    """The basic model of folder in meta info

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

    def _filter_folder(
        self, i: tuple[str, "FileMetaInfo | FolderMetaInfo"]
    ) -> TypeGuard[tuple[str, "FolderMetaInfo"]]:
        return isinstance(i[1], FolderMetaInfo)

    def _filter_file(
        self, i: tuple[str, "FileMetaInfo | FolderMetaInfo"]
    ) -> TypeGuard[tuple[str, FileMetaInfo]]:
        return isinstance(i[1], FileMetaInfo)

    @property
    def _folders(self):
        return filter(self._filter_folder, self.files.items())

    @property
    def _files(self):
        return filter(self._filter_file, self.files.items())

    def walk(
        self, prefix: PurePath | None = None
    ) -> Generator[_WalkReturnType, None, None]:
        if prefix is None:
            prefix = PurePath("./")
        yield prefix, dict(self._folders), dict(self._files)

        for name, meta in self._folders:
            yield from meta.walk(prefix / name)


def to_folder_meta_info(json: FolderMetaDictInfo) -> FolderMetaInfo:
    files: dict[str, FileMetaInfo | FolderMetaInfo] = {}
    for name, item in json.items():
        if list(item.keys()) == ["files"]:
            _logger.debug("Creating folder meta info for %s", name)
            files[name] = to_folder_meta_info(item["files"])  # pyright: ignore
        else:
            _logger.debug("Creating file meta info for %s", name)
            files[name] = _to_file_meta_info(item)  # pyright: ignore
    return FolderMetaInfo(files)
