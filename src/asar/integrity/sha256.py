import hashlib
import logging
from typing import override
from asar.integrity.checker import IntegrityChecker
from asar.models.integrity import IntegrityInfo


_logger = logging.getLogger(__name__)


class Sha256Checker(IntegrityChecker):
    """Check if data matches sha256 checksum."""

    @override
    def check(self, data: bytes, info: IntegrityInfo) -> bool:
        cipher = hashlib.sha256(data)
        if cipher.hexdigest() != info.hash_:
            _logger.error("Hash mismatch!")
            _logger.info("Got %s, wants %s.", cipher.hexdigest(), info.hash_)
            return False
        blocks = [
            data[i : i + info.blocksize] for i in range(0, len(data), info.blocksize)
        ]
        for i in range(len(blocks)):
            cipher = hashlib.sha256(blocks[i])
            if len(info.blocks) < i or cipher.hexdigest() != info.blocks[i]:
                _logger.error("Block %s hash mismatch!")
                _logger.info("Got %s, wants %s.", cipher.hexdigest(), info.blocks[i])
                return False
        return True