"""Generic api of meta info."""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Self
from typing import OrderedDict
from dataclasses import dataclass


@dataclass
class MetaInfo(ABC):
    """Dataclass to store metainfo from json header."""

    @classmethod
    @abstractmethod
    def from_json(cls, json: OrderedDict[Any, Any]) -> Self:
        """Get instance from json."""
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> OrderedDict[Any, Any]:
        """Serialize instance to json."""
        raise NotImplementedError
