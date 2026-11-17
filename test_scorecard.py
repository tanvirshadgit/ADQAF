import unittest

from scorecard import build_scorecard


class TestAnnotatorScorecard(unittest.TestCase):

    def test_scorecard_metrics(self):
        evaluation = {
            "tp": 8,
            "fp": 2,
            "fn": 2,
            "precision": 0.8,
            "recall": 0.8,
            "f1": 0.8,
            "per_file": {},
        }

        result = build_scorecard(
            annotator_id="annotator_001",
            evaluation=evaluation,
        )

        self.assertEqual(result["annotator_id"], "annotator_001")
        self.assertEqual(result["tp"], 8)
        self.assertEqual(result["fp"], 2)
        self.assertEqual(result["fn"], 2)
        self.assertAlmostEqual(result["f1"], 0.8)


if __name__ == "__main__":
    unittest.main()


class TestScorecardFileCount(unittest.TestCase):

    def test_files_evaluated(self):
        evaluation = {
            "files_evaluated": 12,
            "tp": 8,
            "fp": 2,
            "fn": 2,
            "precision": 0.8,
            "recall": 0.8,
            "f1": 0.8,
        }

        result = build_scorecard("annotator_001", evaluation)

        self.assertEqual(result["files_evaluated"], 12)


class TestScorecardQualityStatus(unittest.TestCase):

    def test_pass_status(self):
        from scorecard import calculate_quality_status

        self.assertEqual(
            calculate_quality_status(0.96),
            "PASS"
        )

    def test_review_status(self):
        from scorecard import calculate_quality_status

        self.assertEqual(
            calculate_quality_status(0.90),
            "REVIEW"
        )

    def test_fail_status(self):
        from scorecard import calculate_quality_status

        self.assertEqual(
            calculate_quality_status(0.80),
            "FAIL"
        )

    def test_custom_thresholds(self):
        from scorecard import calculate_quality_status

        self.assertEqual(
            calculate_quality_status(
                0.92,
                pass_threshold=0.90,
                review_threshold=0.75
            ),
            "PASS"
        )


class TestScorecardStatusIntegration(unittest.TestCase):

    def test_build_scorecard_quality_status(self):
        base = {
            "files_evaluated": 10,
            "tp": 10,
            "fp": 0,
            "fn": 0,
            "precision": 1.0,
            "recall": 1.0,
        }

        cases = [
            (0.97, "PASS"),
            (0.90, "REVIEW"),
            (0.80, "FAIL"),
        ]

        for f1, expected in cases:
            with self.subTest(f1=f1):
                evaluation = {**base, "f1": f1}

                result = build_scorecard(
                    "annotator_001",
                    evaluation
                )

                self.assertEqual(
                    result["quality_status"],
                    expected
                )


class TestScorecardCustomThreshold(unittest.TestCase):

    def test_custom_quality_thresholds(self):
        evaluation = {
            "files_evaluated": 10,
            "tp": 9,
            "fp": 1,
            "fn": 1,
            "precision": 0.9,
            "recall": 0.9,
            "f1": 0.9,
        }

        result = build_scorecard(
            annotator_id="annotator_001",
            evaluation=evaluation,
            pass_threshold=0.90,
            review_threshold=0.75,
        )

        self.assertEqual(result["quality_status"], "PASS")


class TestScorecardJSONExport(unittest.TestCase):

    def test_save_scorecard_json(self):
        import json
        import tempfile
        from pathlib import Path
        from scorecard import save_scorecard

        scorecard = {
            "annotator_id": "annotator_001",
            "files_evaluated": 10,
            "tp": 9,
            "fp": 1,
            "fn": 1,
            "precision": 0.9,
            "recall": 0.9,
            "f1": 0.9,
            "quality_status": "REVIEW",
        }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "reports" / "scorecard.json"

            save_scorecard(scorecard, output)

            self.assertTrue(output.exists())

            saved = json.loads(
                output.read_text(encoding="utf-8")
            )

            self.assertEqual(saved, scorecard)
