from abc import ABC, abstractmethod
from asar.models.integrity import IntegrityInfo


class IntegrityChecker(ABC):
    @abstractmethod
    def check(self, data: bytes, info: IntegrityInfo) -> bool:
        """Check if data is valid.

        Args:
           data(bytes): The data to check.
           info(IntegrityInfo): The integrity info.

        Returns:
            bool: If data is valid.
        """
        raise NotImplementedError()