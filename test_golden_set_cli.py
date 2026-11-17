"""Tests for the Golden-Set command-line interface."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).resolve().parent / "golden_set_cli.py"


class TestGoldenSetCLI(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.gt = self.root / "ground_truth"
        self.ann = self.root / "annotator"
        self.output = self.root / "reports" / "evaluation.json"

        self.gt.mkdir()
        self.ann.mkdir()

        (self.gt / "image001.txt").write_text(
            "0 0.5 0.5 0.4 0.4\n",
            encoding="utf-8"
        )
        (self.ann / "image001.txt").write_text(
            "0 0.5 0.5 0.4 0.4\n",
            encoding="utf-8"
        )

    def run_cli(self, iou="0.5"):
        return subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--ground-truth", str(self.gt),
                "--annotations", str(self.ann),
                "--iou", iou,
                "--output", str(self.output),
            ],
            capture_output=True,
            text=True,
        )

    def test_cli_success(self):
        result = self.run_cli()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("F1 Score: 1.0000", result.stdout)

    def test_cli_json_report(self):
        result = self.run_cli()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.output.exists())

        report = json.loads(
            self.output.read_text(encoding="utf-8")
        )

        self.assertEqual(report["tp"], 1)
        self.assertEqual(report["fp"], 0)
        self.assertEqual(report["fn"], 0)

    def test_invalid_iou_threshold(self):
        result = self.run_cli(iou="1.5")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
