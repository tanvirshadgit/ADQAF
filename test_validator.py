import tempfile
import unittest
from pathlib import Path
from validator import validate_dataset

class ValidatorTests(unittest.TestCase):
    def test_detects_invalid_and_duplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'images').mkdir(); (root/'labels').mkdir()
            (root/'images'/'sample.jpg').write_bytes(b'placeholder')
            (root/'labels'/'sample.txt').write_text('0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0.2 0.2\n2 0.95 0.5 0.2 0.2\n')
            report = validate_dataset(root, 2)
            self.assertEqual(report['issue_counts']['DUPLICATE_BOX'], 1)
            self.assertEqual(report['issue_counts']['INVALID_CLASS'], 1)
            self.assertEqual(report['issue_counts']['INVALID_BOX'], 1)


    def test_missing_label_is_reported_as_warning_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            (root / "images" / "negative.jpg").write_bytes(b"placeholder")

            report = validate_dataset(root, 2)

            self.assertEqual(report["images_checked"], 1)
            self.assertEqual(report["issue_counts"]["MISSING_LABEL"], 1)


    def test_missing_label_policy_allow(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            (root / "images" / "negative.jpg").write_bytes(b"test")

            report = validate_dataset(
                root, 2, missing_label_policy="allow"
            )

            self.assertEqual(report["images_checked"], 1)
            self.assertEqual(report["issues_found"], 0)
            self.assertEqual(report["issue_counts"], {})


    def test_numeric_equivalent_duplicate_boxes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            (root / "images" / "sample.jpg").write_bytes(b"test")
            (root / "labels" / "sample.txt").write_text("0 0.5 0.5 0.2 0.2\n0 0.50 0.50 0.20 0.20\n")
            report = validate_dataset(root, 2)
            self.assertEqual(report["issue_counts"].get("DUPLICATE_BOX", 0), 1)


    def test_uppercase_image_extension_not_orphan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            (root / "images" / "sample.JPG").write_bytes(b"test")
            (root / "labels" / "sample.txt").write_text("0 0.5 0.5 0.2 0.2\n")
            report = validate_dataset(root, 2)
            self.assertEqual(report["issues_found"], 0)


    def test_empty_dataset_raises_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            with self.assertRaisesRegex(ValueError, "No images found"):
                validate_dataset(root, 2)


    def test_invalid_class_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "images").mkdir()
            (root / "labels").mkdir()
            (root / "images" / "sample.jpg").write_bytes(b"test")
            for count in (0, -1):
                with self.subTest(class_count=count):
                    with self.assertRaisesRegex(ValueError, "class_count must be positive"):
                        validate_dataset(root, count)

if __name__ == '__main__':
    unittest.main()
