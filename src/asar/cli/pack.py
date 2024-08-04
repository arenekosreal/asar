from pathlib import Path


def pack(
    dir_: Path,
    output: Path,
    ordering: str | None,
    unpack: str | None,
    unpack_dir: str | None,
    exclude_hidden: bool,
):
    raise NotImplementedError("Writing asar is not supported now.")