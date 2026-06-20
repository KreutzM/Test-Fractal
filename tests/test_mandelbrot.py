from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

from core.mandelbrot import RenderParams, colorize_iterations, render_mandelbrot, validate_params


class MandelbrotTests(unittest.TestCase):
    def test_validate_params_accepts_valid_input(self):
        params = validate_params(
            RenderParams(width=32, height=24, max_iterations=20, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0)
        )
        self.assertEqual(params.width, 32)
        self.assertEqual(params.palette, "classic")

    def test_validate_params_rejects_invalid_input(self):
        invalid_cases = [
            RenderParams(width=0, height=24, max_iterations=20, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0),
            RenderParams(width=32, height=-1, max_iterations=20, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0),
            RenderParams(width=32, height=24, max_iterations=0, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0),
            RenderParams(width=32, height=24, max_iterations=20, x_min=1.0, x_max=1.0, y_min=-1.0, y_max=1.0),
            RenderParams(width=32, height=24, max_iterations=20, x_min=-2.0, x_max=1.0, y_min=1.0, y_max=1.0),
            RenderParams(
                width=32,
                height=24,
                max_iterations=20,
                x_min=-2.0,
                x_max=1.0,
                y_min=-1.0,
                y_max=1.0,
                palette="missing",
            ),
        ]

        for params in invalid_cases:
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    validate_params(params)

    def test_iterations_matrix_shape_and_range(self):
        params = validate_params(
            RenderParams(width=40, height=30, max_iterations=25, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0)
        )
        iterations = render_mandelbrot(params)

        self.assertEqual(iterations.shape, (30, 40))
        self.assertTrue(np.issubdtype(iterations.dtype, np.integer))
        self.assertGreaterEqual(iterations.min(), 0)
        self.assertLessEqual(iterations.max(), params.max_iterations)

    def test_all_palettes_return_rgb_arrays(self):
        params = validate_params(
            RenderParams(width=16, height=12, max_iterations=10, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0)
        )
        iterations = render_mandelbrot(params)

        for palette in ("classic", "grayscale", "fire"):
            with self.subTest(palette=palette):
                rgb = colorize_iterations(iterations, params.max_iterations, palette)
                self.assertEqual(rgb.shape, (12, 16, 3))
                self.assertEqual(rgb.dtype, np.uint8)
                self.assertGreaterEqual(int(rgb.min()), 0)
                self.assertLessEqual(int(rgb.max()), 255)

    def test_cli_creates_png_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "mandelbrot.png"
            metadata = tmp_path / "mandelbrot.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "core",
                    "--output",
                    str(output),
                    "--metadata-output",
                    str(metadata),
                    "--width",
                    "48",
                    "--height",
                    "36",
                    "--max-iterations",
                    "30",
                    "--x-min",
                    "-2.2",
                    "--x-max",
                    "0.6",
                    "--y-min",
                    "-1.1",
                    "--y-max",
                    "1.1",
                    "--palette",
                    "fire",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            self.assertTrue(metadata.exists())

            with metadata.open("r", encoding="utf-8") as handle:
                data = json.load(handle)

            self.assertEqual(
                data,
                {
                    "height": 36,
                    "max_iterations": 30,
                    "palette": "fire",
                    "width": 48,
                    "x_max": 0.6,
                    "x_min": -2.2,
                    "y_max": 1.1,
                    "y_min": -1.1,
                },
            )

    def test_cli_rejects_invalid_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "mandelbrot.png"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "core",
                    "--output",
                    str(output),
                    "--palette",
                    "rainbow",
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
