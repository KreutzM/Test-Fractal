from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .mandelbrot import DEFAULT_PARAMS, RenderParams, render_png, validate_params


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="core")
    parser.add_argument("--output", required=True, help="Path to the PNG output file.")
    parser.add_argument("--width", type=int, default=DEFAULT_PARAMS.width)
    parser.add_argument("--height", type=int, default=DEFAULT_PARAMS.height)
    parser.add_argument("--max-iterations", type=int, default=DEFAULT_PARAMS.max_iterations)
    parser.add_argument("--x-min", type=float, default=DEFAULT_PARAMS.x_min)
    parser.add_argument("--x-max", type=float, default=DEFAULT_PARAMS.x_max)
    parser.add_argument("--y-min", type=float, default=DEFAULT_PARAMS.y_min)
    parser.add_argument("--y-max", type=float, default=DEFAULT_PARAMS.y_max)
    parser.add_argument(
        "--palette",
        default=DEFAULT_PARAMS.palette,
        choices=("classic", "grayscale", "fire"),
    )
    parser.add_argument("--metadata-output", help="Optional path for the metadata JSON file.")
    return parser


def _build_params(args: argparse.Namespace) -> RenderParams:
    return validate_params(
        RenderParams(
            width=args.width,
            height=args.height,
            max_iterations=args.max_iterations,
            x_min=args.x_min,
            x_max=args.x_max,
            y_min=args.y_min,
            y_max=args.y_max,
            palette=args.palette,
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    params = _build_params(args)

    render_png(params, args.output)

    if args.metadata_output:
        metadata_path = Path(args.metadata_output)
        metadata_path.write_text(
            json.dumps(params.as_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return 0
