"""API interface to convert meta info in json header back."""

from abc import ABC
from abc import abstractmethod
from typing import Any
from dataclasses import dataclass


@dataclass
class MetaInfo(ABC):
    """Abstract class defines functions required by valid meta info."""

    @abstractmethod
    def to_json(self) -> dict[Any, Any]:
        """Convert instance to json dict."""
        raise NotImplementedError("This is not implemented")
