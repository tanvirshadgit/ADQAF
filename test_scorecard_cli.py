"""Integration tests for the annotator scorecard CLI."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class TestScorecardCLI(unittest.TestCase):

    def test_cli_generates_valid_scorecard(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "scorecard.json"

            gt_dir = Path(directory) / "ground_truth"
            ann_dir = Path(directory) / "annotations"

            gt_dir.mkdir()
            ann_dir.mkdir()

            (gt_dir / "image1.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n",
                encoding="utf-8"
            )
            (ann_dir / "image1.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n",
                encoding="utf-8"
            )

            (gt_dir / "image2.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n",
                encoding="utf-8"
            )
            (ann_dir / "image2.txt").write_text(
                "0 0.1 0.1 0.2 0.2\n",
                encoding="utf-8"
            )

            command = [
                sys.executable,
                str(PROJECT_DIR / "scorecard_cli.py"),
                "--annotator-id", "annotator_001",
                "--ground-truth",
                str(gt_dir),
                "--annotations",
                str(ann_dir),
                "--output", str(output),
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=PROJECT_DIR,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=result.stderr,
            )

            self.assertTrue(output.exists())

            report = json.loads(
                output.read_text(encoding="utf-8")
            )

            self.assertEqual(
                report["annotator_id"],
                "annotator_001",
            )
            self.assertEqual(report["files_evaluated"], 2)
            self.assertEqual(report["tp"], 1)
            self.assertEqual(report["fp"], 1)
            self.assertEqual(report["fn"], 1)
            self.assertAlmostEqual(report["f1"], 0.5)
            self.assertEqual(report["quality_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
