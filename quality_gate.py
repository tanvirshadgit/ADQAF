import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SEVERITY = {
    "INVALID_BOX": "ERROR",
    "INVALID_CLASS": "ERROR",
    "NON_NUMERIC": "ERROR",
    "NON_FINITE": "ERROR",
    "ORPHAN_LABEL": "ERROR",
    "MISSING_LABEL": "WARNING",
    "EMPTY_LABEL": "WARNING",
    "INVALID_FORMAT": "ERROR",
    "DUPLICATE_BOX": "WARNING",
}

def evaluate(report):
    findings = []
    for issue in report["issues"]:
        item = dict(issue)
        item["severity"] = SEVERITY.get(
            issue["code"], "ERROR"
        )
        item["review_status"] = "OPEN"
        findings.append(item)

    counts = Counter(
        item["severity"] for item in findings
    )

    if counts["ERROR"] > 0:
        decision = "FAIL"
    elif counts["WARNING"] > 0:
        decision = "REVIEW"
    else:
        decision = "PASS"

    return {
        "decision": decision,
        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "images_checked": report["images_checked"],
        "total_findings": len(findings),
        "severity_counts": dict(counts),
        "findings": findings,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = json.loads(
        Path(args.report).read_text()
    )

    result = evaluate(report)

    output = Path(args.output)
    output.parent.mkdir(
        parents=True, exist_ok=True
    )
    output.write_text(
        json.dumps(result, indent=2)
    )

    print("Quality Gate:", result["decision"])
    print("Severity:", result["severity_counts"])
    print("Report saved:", output)

if __name__ == "__main__":
    main()
