"""Data struct for integrity info."""

from typing import Self
from typing import Literal
from typing import OrderedDict
from typing import override
from asar.base import MetaInfo
from dataclasses import dataclass


AlgorithmType = Literal["SHA256"]
IntegrityDictInfo = OrderedDict[
    Literal["algorithm", "hash", "blockSize", "blocks"],
    AlgorithmType | str | int | list[str],
]


@dataclass
class IntegrityInfo(MetaInfo):
    """Dataclass to save integrity info."""

    algorithm: AlgorithmType
    hash_: str
    blocksize: int
    blocks: list[str]

    @override
    @classmethod
    def from_json(cls, json: IntegrityDictInfo) -> Self:
        algorithm: AlgorithmType | None = None
        hash_: str | None = None
        blocksize: int | None = None
        blocks: list[str] | None = None
        for k, v in json.items():
            match k:
                case "algorithm":
                    if isinstance(v, str):
                        match v:
                            case "SHA256":
                                algorithm = v
                            case _:
                                raise NotImplementedError("Unsupported algorithm", v)
                    else:
                        raise ValueError("Invalid algorithm", v)
                case "hash":
                    if isinstance(v, str):
                        hash_ = v
                    else:
                        raise ValueError("Invalid hash", v)
                case "blockSize":
                    if isinstance(v, int):
                        blocksize = v
                    else:
                        raise ValueError("Invalid blockSize", v)
                case "blocks":
                    if isinstance(v, list):
                        blocks = v
                    else:
                        raise ValueError("Invalid blocks", v)
        if algorithm is None:
            raise ValueError("No algorithm in json.")
        if hash_ is None:
            raise ValueError("No hash in json.")
        if blocksize is None:
            raise ValueError("No blockSize in json.")
        if blocks is None:
            raise ValueError("No blocks in json.")
        return cls(algorithm, hash_, blocksize, blocks)

    @override
    def to_json(self) -> IntegrityDictInfo:
        json: IntegrityDictInfo = OrderedDict()
        json["algorithm"] = self.algorithm
        json["hash"] = self.hash_
        json["blockSize"] = self.blocksize
        json["blocks"] = self.blocks
        return json
