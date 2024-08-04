import logging
from dataclasses import dataclass
from typing import Literal, override
from asar.models.integrity import (
    IntegrityDictInfo,
    IntegrityInfo,
    to_integrity_info as _to_integrity_info,
)
from asar.models.metainfo import MetaInfo

_logger = logging.getLogger(__name__)

FileMetaDictInfo = dict[
    Literal["size", "offset", "unpacked", "integrity"], int | str | IntegrityDictInfo
]


@dataclass
class FileMetaInfo(MetaInfo):
    """The basic model of file in meta info

    ```json
    {
        "size": <int>,
        // Optional
        "offset": "<int>",
        // Optional
        "unpacked": <bool>,
        "integrity": <IntegrityDictInfo>
    }
    ```
    """

    size: int
    # NOTE: Use int(info.offset) to convert, this is string in raw json
    #       If it is None, this means that file is not in the archive()
    offset: str | None
    integrity: IntegrityInfo | None

    @override
    def to_json(self) -> FileMetaDictInfo:
        base: FileMetaDictInfo = {"size": self.size}
        if self.integrity is not None:
            base["integrity"] = self.integrity.to_json()
        if self.offset is None:
            base["unpacked"] = True
        else:
            base["offset"] = self.offset
        return base


def to_file_meta_info(json: FileMetaDictInfo) -> FileMetaInfo:
    size: int | None = None
    offset: str | None = None
    integrity: IntegrityInfo | None = None
    for key, value in json.items():
        match key:
            case "size":
                if not isinstance(value, int):
                    raise ValueError("Invalid size ", value)
                size = value
            case "offset":
                if not isinstance(value, str):
                    raise ValueError("Invalid offset ", value)
                offset = value
            case "unpacked":
                if not isinstance(value, bool):
                    raise ValueError("Invalid unpack ", value)
                offset = None
            case "integrity":
                if not isinstance(value, dict):
                    raise ValueError("Invalid integrity ", value)
                integrity = _to_integrity_info(value)
    assert size is not None
    if integrity is None:
        _logger.warning("There is no `integrity` value in dict!")
    return FileMetaInfo(size=size, offset=offset, integrity=integrity)