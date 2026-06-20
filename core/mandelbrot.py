from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


DEFAULT_WIDTH = 320
DEFAULT_HEIGHT = 240
DEFAULT_MAX_ITERATIONS = 64


def mandelbrot_iterations(
    width: int,
    height: int,
    *,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
) -> np.ndarray:
    """Return Mandelbrot iteration counts for a regular grid."""

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    x_values = np.linspace(x_min, x_max, width, dtype=np.float64)
    y_values = np.linspace(y_min, y_max, height, dtype=np.float64)
    c = x_values[None, :] + 1j * y_values[:, None]
    z = np.zeros_like(c)
    counts = np.zeros((height, width), dtype=np.uint16)
    active = np.ones((height, width), dtype=bool)

    for iteration in range(max_iterations):
        z[active] = z[active] * z[active] + c[active]
        escaped = np.greater(np.abs(z), 2.0, out=np.zeros_like(active), where=active)
        newly_escaped = active & escaped
        counts[newly_escaped] = iteration + 1
        active &= ~escaped
        if not active.any():
            break

    counts[active] = max_iterations
    return counts


def iterations_to_rgb(iterations: np.ndarray, *, max_iterations: int) -> np.ndarray:
    """Map iteration counts to a Pillow-compatible RGB image array."""

    if iterations.ndim != 2:
        raise ValueError("iterations must be a 2D array")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    normalized = iterations.astype(np.float32) / float(max_iterations)
    red = np.clip(255.0 * normalized, 0, 255).astype(np.uint8)
    green = np.clip(255.0 * np.sqrt(normalized, dtype=np.float32), 0, 255).astype(
        np.uint8
    )
    blue = np.clip(255.0 * (1.0 - normalized), 0, 255).astype(np.uint8)
    return np.stack((red, green, blue), axis=-1)


def save_png(image: np.ndarray, output_path: str | Path) -> Path:
    """Write an RGB array to a PNG file."""

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="RGB").save(target, format="PNG")
    return target


def create_example_image(
    output_path: str | Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> Path:
    """Render and save a deterministic Mandelbrot example image."""

    iterations = mandelbrot_iterations(width, height, max_iterations=max_iterations)
    rgb_image = iterations_to_rgb(iterations, max_iterations=max_iterations)
    return save_png(rgb_image, output_path)
