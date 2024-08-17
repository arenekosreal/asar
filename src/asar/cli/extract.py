"""Extract whole archive or some files inside it."""

import stat
import logging
from asar import Asar
from pathlib import Path
from pathlib import PurePath


_logger = logging.getLogger(__name__)


class ChecksumMismatchError(Exception):
    """Raises when a FileMetaInfo failed to check integrity."""


def extract_file(archive: Path, filename: PurePath):
    """Extract a file in the archive.

    Args:
        archive(Path): The path to asar archive.
        filename(PurePath): The path to the file to extract.
    """
    _logger.info("Extracting file %s to %s...", filename, filename.name)
    filename = filename.relative_to("/")
    asar = Asar(archive.read_bytes())
    if filename.is_absolute():
        filename = filename.relative_to("/")
    target = asar[filename]
    if not target.check():
        raise ChecksumMismatchError
    _ = Path(filename.name).write_bytes(target.content)


def extract(archive: Path, dest: PurePath):
    """Extract archive to the destination.

    Args:
        archive(Path): The path to asar archive.
        dest(PurePath): The destination to store extracted content.
    """
    if not dest.is_absolute():
        dest = PurePath(Path.cwd() / dest)
    _logger.info("Extracting archive to %s...", dest)
    asar = Asar(archive.read_bytes())
    for path, f in asar.items():
        target_path = Path(dest / path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not f.check():
            raise ChecksumMismatchError
        _ = target_path.write_bytes(f.content)
        if f.meta.executable:
            target_path.chmod(stat.S_IXOTH | stat.S_IXGRP | stat.S_IXUSR)
