from __future__ import annotations

import sys

from agent_orchestrator.cli import build_parser as _orchestrator_build_parser
from agent_orchestrator.cli import main as _orchestrator_main

from . import __version__

build_parser = _orchestrator_build_parser

__all__ = ["build_parser", "main"]


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if "--version" in argv:
        print(__version__)
        return 0

    return _orchestrator_main(argv)
