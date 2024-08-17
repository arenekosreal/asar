"""List content in the archive."""

from asar import Asar
from pathlib import Path


def list_archive(archive: Path, is_pack: bool):
    """List content in the archive.

    Args:
        archive(Path): The path to the asar archive.
        is_pack(bool): If mark the file is packed in archive.
    """
    asar = Asar(archive.read_bytes())
    for path in sorted(asar.files + asar.folders):
        if path in asar and asar[path].meta.offset is None:
            head = "    :" if is_pack else ""
        else:
            head = "packed    :" if is_pack else ""
        print(head, "/" / path)
