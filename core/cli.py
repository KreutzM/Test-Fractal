from __future__ import annotations

import argparse
import sys

from agent_orchestrator.cli import build_parser as _orchestrator_build_parser
from agent_orchestrator.cli import main as _orchestrator_main

from . import __version__

build_parser = _orchestrator_build_parser

__all__ = ["build_parser", "main"]


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    version_parser = argparse.ArgumentParser(add_help=False)
    version_parser.add_argument("--version", action="version", version=__version__)
    version_parser.parse_known_args(argv)

    return _orchestrator_main(argv)
