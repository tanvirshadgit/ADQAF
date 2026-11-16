import unittest
from quality_gate import evaluate


class QualityGateTests(unittest.TestCase):

    def make_report(self, codes):
        return {
            "images_checked": 10,
            "issues": [
                {"code": code, "image": "test.jpg"}
                for code in codes
            ]
        }

    def test_pass_no_issues(self):
        result = evaluate(self.make_report([]))
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["total_findings"], 0)

    def test_review_warnings_only(self):
        result = evaluate(
            self.make_report(["MISSING_LABEL"])
        )
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(
            result["severity_counts"]["WARNING"], 1
        )

    def test_fail_blocking_error(self):
        result = evaluate(
            self.make_report([
                "MISSING_LABEL",
                "ORPHAN_LABEL"
            ])
        )
        self.assertEqual(result["decision"], "FAIL")
        self.assertEqual(
            result["severity_counts"]["ERROR"], 1
        )

    def test_unknown_issue_blocks(self):
        result = evaluate(
            self.make_report(["UNKNOWN_ISSUE"])
        )
        self.assertEqual(result["decision"], "FAIL")


if __name__ == "__main__":
    unittest.main()
