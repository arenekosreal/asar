import logging
from pathlib import Path, PurePath
from asar import Asar
from asar.models.file import FileMetaInfo


_logger = logging.getLogger(__name__)


def extract_file(archive: Path, filename: PurePath):
    _logger.info("Extracting file %s to %s...", filename, filename.name)
    filename = filename.relative_to("/")
    asar = Asar(archive.read_bytes())
    info = asar.at(filename)
    if isinstance(info, FileMetaInfo):
        content = asar.get_file(info)
        _ = Path(filename.name).write_bytes(content)
    else:
        raise TypeError("Give filename is not a file.")


def extract(archive: Path, dest: PurePath):
    if not dest.is_absolute():
        dest = PurePath(Path.cwd() / dest)
    _logger.info("Extracting archive to %s...", dest)
    asar = Asar(archive.read_bytes())
    Path(dest).mkdir(parents=True, exist_ok=True)
    for root, folders, files in asar.meta.walk():
        for name in folders.keys():
            folder = Path(dest / root / name)
            folder.mkdir(parents=True, exist_ok=True)
        for name in files.keys():
            f = Path(dest / root / name)
            f.parent.mkdir(parents=True, exist_ok=True)
            internal_path = "/" / f.relative_to(dest)
            info = asar.at(internal_path)
            if isinstance(info, FileMetaInfo):
                _ = f.write_bytes(asar.get_file(info))
            else:
                raise TypeError("Give path %s is not a file.", internal_path)
