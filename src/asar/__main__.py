from argparse import ArgumentParser
from pathlib import Path, PurePath
from typing import Literal
from asar import __version__
from asar.cli.extract import extract as _extract, extract_file as _extract_file
from asar.cli.list import list_archive as _list
from asar.cli.pack import pack as _pack


_ArgsCommandType = Literal[
    "pack", "p", "list", "l", "extract-file", "ef", "extract", "e"
]


def _create_pack_handler(parser: ArgumentParser) -> ArgumentParser:
    _ = parser.add_argument("dir", type=Path)
    _ = parser.add_argument("output", type=Path)
    _ = parser.add_argument(
        "--ordering", type=Path, help="path to a text file for ordering contents"
    )
    _ = parser.add_argument(
        "--unpack", help="do not pack files matching glob expression <UNPACK>"
    )
    _ = parser.add_argument(
        "--unpack-dir",
        help="do not pack dirs matching glob expression <UNPACK_DIR> or starting with literal expression <UNPACK_DIR>",
    )
    _ = parser.add_argument(
        "--exclude-hidden", action="store_true", help="exclude hidden files"
    )
    return parser


def _create_list_handler(parser: ArgumentParser) -> ArgumentParser:
    _ = parser.add_argument("archive", type=Path)
    _ = parser.add_argument(
        "--is-pack",
        "-i",
        action="store_true",
        help="each file in the asar is pack or unpack",
    )
    return parser


def _create_extract_file_handler(parser: ArgumentParser) -> ArgumentParser:
    _ = parser.add_argument("archive", type=Path)
    _ = parser.add_argument("filename", type=PurePath)
    return parser


def _create_extract_handler(parser: ArgumentParser) -> ArgumentParser:
    _ = parser.add_argument("archive", type=Path)
    _ = parser.add_argument("dest", type=PurePath)
    return parser


def main():
    parser = ArgumentParser()
    _ = parser.add_argument(
        "-v", "--version", action="store_true", help="show version info"
    )
    sparser = parser.add_subparsers(title="Commands", dest="command")
    pack = sparser.add_parser("pack", aliases=["p"], help="create asar archive")
    pack = _create_pack_handler(pack)
    ls = sparser.add_parser("list", aliases=["l"], help="list files of asar archive")
    ls = _create_list_handler(ls)
    ef = sparser.add_parser(
        "extract-file", aliases=["ef"], help=" extract one file from archive"
    )
    ef = _create_extract_file_handler(ef)
    e = sparser.add_parser("extract", aliases=["e"], help="extract archive")
    e = _create_extract_handler(e)
    args = parser.parse_args()
    if args.version:
        print(__version__)
    else:
        command: _ArgsCommandType = args.command
        match command:
            case "pack" | "p":
                _pack(
                    args.dir,
                    args.output,
                    args.ordering,
                    args.unpack,
                    args.unpack_dir,
                    args.exclude_hidden,
                )
            case "list" | "l":
                _list(args.archive, args.is_pack)
            case "extract-file" | "ef":
                _extract_file(args.archive, args.filename)
            case "extract" | "e":
                _extract(args.archive, args.dest)


if __name__ == "__main__":
    # python -m asar ...
    main()

__all__ = ["main"]
