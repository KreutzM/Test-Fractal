from __future__ import annotations

import argparse
from pathlib import Path

from .mandelbrot import DEFAULT_HEIGHT, DEFAULT_MAX_ITERATIONS, DEFAULT_WIDTH, create_example_image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="core")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mandelbrot.png"),
        help="Path for the generated PNG file.",
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--max-iterations", type=int, default=DEFAULT_MAX_ITERATIONS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    create_example_image(
        args.output,
        width=args.width,
        height=args.height,
        max_iterations=args.max_iterations,
    )
    return 0
