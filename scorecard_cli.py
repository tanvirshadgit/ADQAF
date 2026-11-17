"""Command-line interface for ADQAF Annotator Scorecards."""

import argparse
from pathlib import Path

from golden_set import evaluate_annotation_directories
from scorecard import build_scorecard, save_scorecard


def main():
    parser = argparse.ArgumentParser(
        description="Generate an annotator performance scorecard"
    )

    parser.add_argument("--annotator-id", required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--pass-threshold", type=float, default=0.95)
    parser.add_argument("--review-threshold", type=float, default=0.85)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/scorecard/scorecard.json")
    )

    args = parser.parse_args()

    evaluation = evaluate_annotation_directories(
        args.ground_truth,
        args.annotations,
        iou_threshold=args.iou
    )

    result = build_scorecard(
        annotator_id=args.annotator_id,
        evaluation=evaluation,
        pass_threshold=args.pass_threshold,
        review_threshold=args.review_threshold
    )

    output = save_scorecard(result, args.output)

    print("Annotator:", result["annotator_id"])
    print("Files evaluated:", result["files_evaluated"])
    print("TP:", result["tp"])
    print("FP:", result["fp"])
    print("FN:", result["fn"])
    print(f"Precision: {result['precision']:.4f}")
    print(f"Recall: {result['recall']:.4f}")
    print(f"F1 Score: {result['f1']:.4f}")
    print("Quality Status:", result["quality_status"])
    print("Report saved:", output)


if __name__ == "__main__":
    main()
