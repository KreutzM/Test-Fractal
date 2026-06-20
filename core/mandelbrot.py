from __future__ import annotations

from numbers import Integral
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class RenderParams:
    width: int = 800
    height: int = 600
    max_iterations: int = 100
    x_min: float = -2.0
    x_max: float = 1.0
    y_min: float = -1.5
    y_max: float = 1.5
    palette: str = "classic"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


DEFAULT_PARAMS = RenderParams()

_PALETTE_STOPS: dict[str, np.ndarray] = {
    "classic": np.array(
        [
            [0, 7, 100],
            [32, 107, 203],
            [237, 255, 255],
            [255, 170, 0],
            [0, 2, 0],
        ],
        dtype=np.float64,
    ),
    "grayscale": np.array(
        [
            [0, 0, 0],
            [255, 255, 255],
        ],
        dtype=np.float64,
    ),
    "fire": np.array(
        [
            [0, 0, 0],
            [90, 0, 0],
            [200, 30, 0],
            [255, 140, 0],
            [255, 255, 255],
        ],
        dtype=np.float64,
    ),
}

PALETTE_NAMES = tuple(_PALETTE_STOPS)


def _is_int_like(value: object) -> bool:
    return isinstance(value, Integral) and not isinstance(value, bool)


def validate_params(params: RenderParams) -> RenderParams:
    if not _is_int_like(params.width):
        raise ValueError("width must be an integer")
    if not _is_int_like(params.height):
        raise ValueError("height must be an integer")
    if not _is_int_like(params.max_iterations):
        raise ValueError("max_iterations must be an integer")
    if params.width <= 0:
        raise ValueError("width must be positive")
    if params.height <= 0:
        raise ValueError("height must be positive")
    if params.max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if params.x_min >= params.x_max:
        raise ValueError("x_min must be smaller than x_max")
    if params.y_min >= params.y_max:
        raise ValueError("y_min must be smaller than y_max")
    palette = params.palette.lower()
    if palette not in _PALETTE_STOPS:
        raise ValueError(f"unknown palette: {params.palette}")
    return RenderParams(
        width=params.width,
        height=params.height,
        max_iterations=params.max_iterations,
        x_min=params.x_min,
        x_max=params.x_max,
        y_min=params.y_min,
        y_max=params.y_max,
        palette=palette,
    )


def render_mandelbrot(params: RenderParams) -> np.ndarray:
    params = validate_params(params)

    x_values = np.linspace(params.x_min, params.x_max, params.width, dtype=np.float64)
    y_values = np.linspace(params.y_min, params.y_max, params.height, dtype=np.float64)
    c = x_values[np.newaxis, :] + 1j * y_values[:, np.newaxis]
    z = np.zeros_like(c)
    iterations = np.zeros((params.height, params.width), dtype=np.int32)
    active = np.ones((params.height, params.width), dtype=bool)

    for iteration in range(params.max_iterations):
        z[active] = z[active] * z[active] + c[active]
        escaped = np.greater(np.abs(z), 2.0)
        newly_escaped = escaped & active
        iterations[newly_escaped] = iteration + 1
        active &= ~escaped
        if not active.any():
            break

    iterations[active] = params.max_iterations
    return iterations


def _sample_gradient(stops: np.ndarray, values: np.ndarray) -> np.ndarray:
    scaled = values * (len(stops) - 1)
    lower = np.floor(scaled).astype(np.int64)
    upper = np.clip(lower + 1, 0, len(stops) - 1)
    fraction = (scaled - lower)[..., np.newaxis]
    lower = np.clip(lower, 0, len(stops) - 1)

    colors = stops[lower] * (1.0 - fraction) + stops[upper] * fraction
    return np.clip(colors, 0, 255)


def colorize_iterations(iterations: np.ndarray, max_iterations: int, palette: str) -> np.ndarray:
    palette_key = palette.lower()
    if palette_key not in _PALETTE_STOPS:
        raise ValueError(f"unknown palette: {palette}")

    normalized = np.clip(iterations.astype(np.float64) / max_iterations, 0.0, 1.0)
    rgb = _sample_gradient(_PALETTE_STOPS[palette_key], normalized)
    rgb[iterations >= max_iterations] = 0
    return rgb.astype(np.uint8)


def render_png(params: RenderParams, output_path: str | Path) -> np.ndarray:
    iterations = render_mandelbrot(params)
    rgb = colorize_iterations(iterations, params.max_iterations, params.palette)
    image = Image.fromarray(rgb, mode="RGB")
    image.save(output_path)
    return rgb
