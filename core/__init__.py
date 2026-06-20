"""Minimal Mandelbrot renderer package."""

from .mandelbrot import (
    create_example_image,
    mandelbrot_iterations,
    iterations_to_rgb,
    save_png,
)

__all__ = [
    "create_example_image",
    "mandelbrot_iterations",
    "iterations_to_rgb",
    "save_png",
]
