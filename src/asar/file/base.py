"""Classes describing file in asar archive."""

from typing import Self
from typing import Literal
from typing import OrderedDict
from typing import override
from asar.base import MetaInfo
from dataclasses import dataclass
from asar.integrity.base import AlgorithmType
from asar.integrity.base import IntegrityInfo
from asar.integrity.base import IntegrityDictInfo
from asar.integrity.sha256 import Sha256Checker
from asar.integrity.checker import IntegrityChecker


FileMetaDictInfo = OrderedDict[
    Literal["offset", "size", "unpacked", "executable", "integrity"],
    str | int | bool | IntegrityDictInfo,
]


@dataclass
class FileMetaInfo(MetaInfo):
    """Dataclass to save metainfo for a file in archive."""

    offset: str | None
    size: int
    executable: bool
    integrity: IntegrityInfo

    @override
    @classmethod
    def from_json(cls, json: FileMetaDictInfo) -> Self:
        offset: str | None = None
        size: int | None = None
        executable = False
        integrity: IntegrityInfo | None = None
        for k, v in json.items():
            match k:
                case "offset":
                    if isinstance(v, str):
                        offset = v
                    else:
                        raise ValueError("Invalid offset", v)
                case "size":
                    if isinstance(v, int):
                        size = v
                    else:
                        raise ValueError("Invalid size", v)
                case "unpacked":
                    if isinstance(v, bool):
                        if v:
                            size = None
                    else:
                        raise ValueError("Invalid unpacked", v)
                case "executable":
                    if isinstance(v, bool):
                        executable = v
                    else:
                        raise ValueError("Invalid executable", v)
                case "integrity":
                    if isinstance(v, dict):
                        integrity = IntegrityInfo.from_json(v)
                    else:
                        raise ValueError("Invalid integrity", v)
        if size is None:
            raise ValueError("No size in json.")
        if integrity is None:
            raise ValueError("No integrity in json.")
        return cls(offset, size, executable, integrity)

    @override
    def to_json(self) -> FileMetaDictInfo:
        json: FileMetaDictInfo = OrderedDict()
        if self.offset is not None:
            json["offset"] = self.offset
        json["size"] = self.size
        if self.offset is None:
            json["unpacked"] = True
        if self.executable:
            json["executable"] = self.executable
        json["integrity"] = self.integrity.to_json()
        return json

    @property
    def unpacked(self) -> bool:
        """If this file is not contained in the archive."""
        return self.offset is None


@dataclass
class AsarFile:
    """Dataclass to save a file in archive."""

    meta: FileMetaInfo
    content: bytes

    @staticmethod
    def _get_checkers(checksum: AlgorithmType) -> IntegrityChecker:
        known_checkers: dict[AlgorithmType, IntegrityChecker] = {
            "SHA256": Sha256Checker(),
        }
        return known_checkers[checksum]

    def check(self) -> bool:
        """Check integrity."""
        checker = AsarFile._get_checkers(self.meta.integrity.algorithm)
        return checker.check(self.content, self.meta.integrity)
