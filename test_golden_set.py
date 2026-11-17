import unittest

from golden_set import calculate_iou, match_annotations


class TestGoldenSetIoU(unittest.TestCase):

    def test_identical_boxes(self):
        box = (0.5, 0.5, 0.4, 0.4)
        self.assertAlmostEqual(calculate_iou(box, box), 1.0)

    def test_non_overlapping_boxes(self):
        a = (0.2, 0.2, 0.2, 0.2)
        b = (0.8, 0.8, 0.2, 0.2)
        self.assertAlmostEqual(calculate_iou(a, b), 0.0)

    def test_partially_overlapping_boxes(self):
        a = (0.4, 0.5, 0.4, 0.4)
        b = (0.6, 0.5, 0.4, 0.4)
        self.assertAlmostEqual(calculate_iou(a, b), 1 / 3)

    def test_zero_width(self):
        with self.assertRaises(ValueError):
            calculate_iou(
                (0.5, 0.5, 0.0, 0.4),
                (0.5, 0.5, 0.4, 0.4)
            )

    def test_non_finite_coordinates(self):
        with self.assertRaises(ValueError):
            calculate_iou(
                (float('nan'), 0.5, 0.4, 0.4),
                (0.5, 0.5, 0.4, 0.4)
            )


if __name__ == '__main__':
    unittest.main()


class TestGoldenSetMatching(unittest.TestCase):

    def setUp(self):
        self.box = (0, 0.5, 0.5, 0.4, 0.4)

    def test_perfect_match(self):
        result = match_annotations([self.box], [self.box])
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (1, 0, 0))
        self.assertEqual(result["f1"], 1.0)

    def test_wrong_class(self):
        wrong_class = (1, 0.5, 0.5, 0.4, 0.4)
        result = match_annotations([self.box], [wrong_class])
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (0, 1, 1))

    def test_duplicate_annotation(self):
        result = match_annotations([self.box], [self.box, self.box])
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (1, 1, 0))

    def test_missing_annotation(self):
        result = match_annotations([self.box], [])
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (0, 0, 1))

    def test_empty_ground_truth(self):
        result = match_annotations([], [self.box])
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (0, 1, 0))

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            match_annotations([self.box], [self.box], iou_threshold=1.5)


class TestGoldenSetReporting(unittest.TestCase):

    def test_save_and_read_json_report(self):
        import json
        import tempfile
        from pathlib import Path
        from golden_set import save_evaluation_report

        result = {
            "evaluation_type": "golden_set",
            "iou_threshold": 0.5,
            "tp": 1,
            "fp": 0,
            "fn": 0,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0
        }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "evaluation.json"

            saved_path = save_evaluation_report(result, output)

            self.assertTrue(saved_path.exists())

            loaded = json.loads(saved_path.read_text(encoding="utf-8"))

            self.assertEqual(loaded, result)


class TestYOLOAnnotationReader(unittest.TestCase):

    def test_valid_annotations(self):
        import tempfile
        from pathlib import Path
        from golden_set import read_yolo_annotations

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.txt"
            path.write_text(
                "0 0.5 0.5 0.4 0.4\n"
                "1 0.3 0.3 0.2 0.2\n",
                encoding="utf-8"
            )

            result = read_yolo_annotations(path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (0, 0.5, 0.5, 0.4, 0.4))

    def test_invalid_format(self):
        import tempfile
        from pathlib import Path
        from golden_set import read_yolo_annotations

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.txt"
            path.write_text("0 0.5 0.5\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_yolo_annotations(path)

    def test_invalid_class(self):
        import tempfile
        from pathlib import Path
        from golden_set import read_yolo_annotations

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.txt"
            path.write_text("-1 0.5 0.5 0.4 0.4\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_yolo_annotations(path)

    def test_invalid_box(self):
        import tempfile
        from pathlib import Path
        from golden_set import read_yolo_annotations

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.txt"
            path.write_text("0 0.9 0.9 0.5 0.5\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_yolo_annotations(path)

    def test_non_finite_value(self):
        import tempfile
        from pathlib import Path
        from golden_set import read_yolo_annotations

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labels.txt"
            path.write_text("0 nan 0.5 0.4 0.4\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_yolo_annotations(path)


class TestGoldenSetFileEvaluation(unittest.TestCase):

    def test_file_evaluation_metrics(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_files

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ground_truth = root / "ground_truth.txt"
            annotator = root / "annotator.txt"

            ground_truth.write_text(
                "0 0.5 0.5 0.4 0.4\n"
                "1 0.3 0.3 0.2 0.2\n",
                encoding="utf-8"
            )

            annotator.write_text(
                "0 0.5 0.5 0.4 0.4\n"
                "2 0.3 0.3 0.2 0.2\n",
                encoding="utf-8"
            )

            result = evaluate_annotation_files(
                ground_truth,
                annotator,
                iou_threshold=0.5
            )

            self.assertEqual(result["tp"], 1)
            self.assertEqual(result["fp"], 1)
            self.assertEqual(result["fn"], 1)
            self.assertAlmostEqual(result["precision"], 0.5)
            self.assertAlmostEqual(result["recall"], 0.5)
            self.assertAlmostEqual(result["f1"], 0.5)

    def test_missing_annotation_file(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_files

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ground_truth = root / "ground_truth.txt"
            ground_truth.write_text(
                "0 0.5 0.5 0.4 0.4\n",
                encoding="utf-8"
            )

            with self.assertRaises(FileNotFoundError):
                evaluate_annotation_files(
                    ground_truth,
                    root / "missing.txt"
                )


class TestGoldenSetDatasetEvaluation(unittest.TestCase):

    def test_multiple_files(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_directories

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gt = root / "ground_truth"
            ann = root / "annotator"
            gt.mkdir()
            ann.mkdir()

            (gt / "image001.txt").write_text(
                "0 0.5 0.5 0.4 0.4\n",
                encoding="utf-8"
            )
            (ann / "image001.txt").write_text(
                "0 0.5 0.5 0.4 0.4\n",
                encoding="utf-8"
            )

            (gt / "image002.txt").write_text(
                "1 0.3 0.3 0.2 0.2\n",
                encoding="utf-8"
            )
            (ann / "image002.txt").write_text(
                "2 0.3 0.3 0.2 0.2\n",
                encoding="utf-8"
            )

            result = evaluate_annotation_directories(gt, ann)

            self.assertEqual(result["files_evaluated"], 2)
            self.assertEqual(result["tp"], 1)
            self.assertEqual(result["fp"], 1)
            self.assertEqual(result["fn"], 1)
            self.assertAlmostEqual(result["f1"], 0.5)

    def test_missing_annotation_file(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_directories

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gt = root / "ground_truth"
            ann = root / "annotator"
            gt.mkdir()
            ann.mkdir()

            (gt / "image001.txt").write_text(
                "0 0.5 0.5 0.4 0.4\n",
                encoding="utf-8"
            )

            result = evaluate_annotation_directories(gt, ann)

            self.assertEqual(result["tp"], 0)
            self.assertEqual(result["fp"], 0)
            self.assertEqual(result["fn"], 1)
            self.assertFalse(
                result["per_file"][0]["annotation_file_present"]
            )

    def test_empty_directories(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_directories

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gt = root / "ground_truth"
            ann = root / "annotator"
            gt.mkdir()
            ann.mkdir()

            with self.assertRaises(ValueError):
                evaluate_annotation_directories(gt, ann)


class TestMissingGroundTruthSafety(unittest.TestCase):

    def test_missing_ground_truth_raises_error(self):
        import tempfile
        from pathlib import Path
        from golden_set import evaluate_annotation_directories

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gt = root / "ground_truth"
            ann = root / "annotator"
            gt.mkdir()
            ann.mkdir()

            (ann / "image001.txt").write_text(
                "0 0.5 0.5 0.4 0.4\n",
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError, "Missing ground-truth files"
            ):
                evaluate_annotation_directories(gt, ann)


class TestMaximumCardinalityMatching(unittest.TestCase):

    def test_greedy_matching_limitation(self):
        from golden_set import match_annotations

        ground_truth = [
            (0, 0.50, 0.50, 0.40, 0.20),
            (0, 0.65, 0.50, 0.40, 0.20),
        ]

        annotations = [
            (0, 0.56, 0.50, 0.40, 0.20),
            (0, 0.40, 0.50, 0.40, 0.20),
        ]

        result = match_annotations(
            ground_truth,
            annotations,
            iou_threshold=0.5
        )

        self.assertEqual(result["tp"], 2)
        self.assertEqual(result["fp"], 0)
        self.assertEqual(result["fn"], 0)
