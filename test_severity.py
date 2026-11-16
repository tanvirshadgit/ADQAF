import unittest
from quality_gate import evaluate


class SeverityTests(unittest.TestCase):

    def make_report(self, code):
        return {
            "images_checked": 1,
            "issues": [
                {
                    "image": "test.jpg",
                    "line": 1,
                    "code": code,
                    "detail": "Test finding"
                }
            ]
        }

    def test_empty_label_warning(self):
        result = evaluate(
            self.make_report("EMPTY_LABEL")
        )
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(
            result["severity_counts"]["WARNING"], 1
        )

    def test_invalid_format_error(self):
        result = evaluate(
            self.make_report("INVALID_FORMAT")
        )
        self.assertEqual(result["decision"], "FAIL")
        self.assertEqual(
            result["severity_counts"]["ERROR"], 1
        )


if __name__ == "__main__":
    unittest.main()
