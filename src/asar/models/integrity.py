"""Data class to store integrity info in json header."""

from typing import Literal
from typing import override
from dataclasses import dataclass
from asar.models.metainfo import MetaInfo


AlgorithmType = Literal["SHA256"]  # TODO: more algorithms
IntegrityDictInfo = dict[
    Literal["algorithm", "hash", "blockSize", "blocks"],
    AlgorithmType | str | int | list[str],
]


@dataclass
class IntegrityInfo(MetaInfo):
    """The basic model of `integrity` part in file meta info.

    ```json
    {
        "algorithm": "SHA256",
        "hash": "<sha256sum>",
        "blockSize": <int>,
        "blocks": [
            "<sha256sum of each block>"
        ]
    }
    """

    algorithm: AlgorithmType
    hash_: str
    blocksize: int
    blocks: list[str]

    @override
    def to_json(self) -> IntegrityDictInfo:
        return {
            "algorithm": self.algorithm,
            "hash": self.hash_,
            "blockSize": self.blocksize,
            "blocks": self.blocks,
        }


def to_integrity_info(json: IntegrityDictInfo) -> IntegrityInfo:
    """Generate IntegrityInfo from IntegrityDictInfo."""
    algorithm: AlgorithmType | None = None
    hash_: str | None = None
    blocksize: int | None = None
    blocks: list[str] | None = None
    for key, value in json.items():
        match key:
            case "algorithm":
                if not isinstance(value, str):
                    raise ValueError("Invalid algorithm ", value)
                match value:
                    case "SHA256":  # TODO Add more algorithms here
                        algorithm = value
                    case _:
                        raise NotImplementedError("Unsupported algorithm ", value)
            case "hash":
                if not isinstance(value, str):
                    raise ValueError("Invalid hash ", value)
                hash_ = value
            case "blockSize":
                if not isinstance(value, int):
                    raise ValueError("Invalid blockSize ", value)
                blocksize = value
            case "blocks":
                if not isinstance(value, list):
                    raise ValueError("Invalid blocks ", value)
                blocks = value

    assert algorithm is not None
    assert hash_ is not None
    assert blocksize is not None
    assert blocks is not None
    return IntegrityInfo(
        algorithm=algorithm,
        hash_=hash_,
        blocksize=blocksize,
        blocks=blocks,
    )
