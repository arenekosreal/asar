"""Pack a folder into the archive."""

from pathlib import Path


def pack(
    dir_: Path,
    output: Path,
    ordering: Path | None,
    unpack: str | None,
    unpack_dir: str | None,
    exclude_hidden: bool,
):
    """Pack a folder into the archive.

    Args:
        dir_(Path): The folder to pack.
        output(Path): The path to generated archive.
        ordering(Path | None): The path to a text file for ordering contents.
        unpack(str | None): The pattern which files will be skipped to pack.
        unpack_dir(str | None): The pattern which directories will be skipped to pack.
        exclude_hidden(bool): If skip packing hidden files.
    """
    raise NotImplementedError("Writing asar is not supported now.")
