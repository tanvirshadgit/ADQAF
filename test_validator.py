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

if __name__ == '__main__':
    unittest.main()
