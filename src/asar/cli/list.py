from pathlib import Path
from asar import Asar


def list_archive(archive: Path, is_pack: bool):
    asar = Asar(archive.read_bytes())
    for path, folders, files in asar.meta.walk():
        for f in folders:
            head = "packed    :"
            print(head, "/" / path / f)
        for f in files:
            if files[f].offset is None:
                head = "    :"
            else:
                head = "packed    :"
            print(head, "/" / path / f)
