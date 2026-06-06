"""Command line interface for ProcessPI."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version


def _package_version() -> str:
    try:
        return version("processpi")
    except PackageNotFoundError:
        from processpi import __version__

        return __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="processpi",
        description="ProcessPI command line entry point for package diagnostics.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"processpi {_package_version()}",
        help="Show the installed ProcessPI version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "doctor",
        help="Check that the package imports and report the installed version.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print(f"ProcessPI {_package_version()} is importable.")
        return 0
    print("ProcessPI command line interface")
    print("Use 'processpi doctor' for an import check or 'processpi --help' for options.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
