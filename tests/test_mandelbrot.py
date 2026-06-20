from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from core.mandelbrot import (
    create_example_image,
    iterations_to_rgb,
    mandelbrot_iterations,
    save_png,
)


class MandelbrotRendererTests(unittest.TestCase):
    def test_iteration_array_shape(self):
        iterations = mandelbrot_iterations(32, 24, max_iterations=20)

        self.assertEqual((24, 32), iterations.shape)

    def test_iteration_values_stay_within_range(self):
        iterations = mandelbrot_iterations(32, 24, max_iterations=20)

        self.assertGreaterEqual(iterations.min(), 0)
        self.assertLessEqual(iterations.max(), 20)

    def test_rgb_output_shape_is_deterministic(self):
        iterations = mandelbrot_iterations(16, 10, max_iterations=12)
        rgb = iterations_to_rgb(iterations, max_iterations=12)

        self.assertEqual((10, 16, 3), rgb.shape)
        self.assertEqual(np.uint8, rgb.dtype)

    def test_png_file_is_created_and_readable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "mandelbrot.png"
            created_path = create_example_image(output_path, width=40, height=30, max_iterations=18)

            self.assertTrue(created_path.exists())
            with Image.open(created_path) as image:
                self.assertEqual((40, 30), image.size)
                self.assertEqual("RGB", image.mode)

    def test_save_png_writes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "manual.png"
            iterations = mandelbrot_iterations(8, 6, max_iterations=10)
            rgb = iterations_to_rgb(iterations, max_iterations=10)

            created_path = save_png(rgb, output_path)

            self.assertTrue(created_path.exists())
            self.assertGreater(created_path.stat().st_size, 0)

