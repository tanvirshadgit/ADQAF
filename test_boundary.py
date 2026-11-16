import tempfile
import unittest
from pathlib import Path

from validator import validate_dataset


class BoundaryTests(unittest.TestCase):

    def check_box(self, annotation):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            labels = root / "labels"

            images.mkdir()
            labels.mkdir()

            (images / "test.jpg").write_bytes(b"test")
            (labels / "test.txt").write_text(
                annotation + "\n"
            )

            report = validate_dataset(root, 80)

            return [
                issue["code"]
                for issue in report["issues"]
            ]

    def test_valid_box(self):
        codes = self.check_box(
            "0 0.5 0.5 0.4 0.4"
        )
        self.assertNotIn("INVALID_BOX", codes)

    def test_rounding_tolerance(self):
        codes = self.check_box(
            "0 0.204596 0.5 0.409193 0.4"
        )
        self.assertNotIn("INVALID_BOX", codes)

    def test_out_of_bounds_box(self):
        codes = self.check_box(
            "0 0.2 0.5 0.42 0.4"
        )
        self.assertIn("INVALID_BOX", codes)

    def test_zero_width_box(self):
        codes = self.check_box(
            "0 0.5 0.5 0.0 0.4"
        )
        self.assertIn("INVALID_BOX", codes)


if __name__ == "__main__":
    unittest.main()
