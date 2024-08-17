"""API interface to check integrity."""

from abc import ABC
from abc import abstractmethod
from asar.integrity.base import IntegrityInfo


class IntegrityChecker(ABC):
    """Abstract class defines functions required by valid checkers."""

    @abstractmethod
    def check(self, data: bytes, info: IntegrityInfo) -> bool:
        """Check if data is valid.

        Args:
           data(bytes): The data to check.
           info(IntegrityInfo): The integrity info.

        Returns:
            bool: If data is valid.
        """
        raise NotImplementedError
