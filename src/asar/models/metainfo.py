from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class MetaInfo(ABC):
    @abstractmethod
    def to_json(self) -> dict[Any, Any]:
        """Convert instance to json dict."""
        raise NotImplementedError("This is not implemented")