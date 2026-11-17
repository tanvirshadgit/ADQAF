"""Command-line interface for ADQAF Golden-Set Evaluation."""

import argparse
from pathlib import Path

from golden_set import (
    evaluate_annotation_directories,
    save_evaluation_report,
)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate YOLO annotations against a golden set"
    )

    parser.add_argument(
        "--ground-truth",
        type=Path,
        required=True,
        help="Directory containing verified ground-truth labels",
    )

    parser.add_argument(
        "--annotations",
        type=Path,
        required=True,
        help="Directory containing annotator labels",
    )

    parser.add_argument(
        "--iou",
        type=float,
        default=0.5,
        help="IoU matching threshold (default: 0.5)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/golden_set/evaluation.json"),
        help="Output JSON report path",
    )

    args = parser.parse_args()

    result = evaluate_annotation_directories(
        args.ground_truth,
        args.annotations,
        iou_threshold=args.iou,
    )

    output = save_evaluation_report(result, args.output)

    print("Files evaluated:", result["files_evaluated"])
    print("TP:", result["tp"])
    print("FP:", result["fp"])
    print("FN:", result["fn"])
    print(f"Precision: {result['precision']:.4f}")
    print(f"Recall: {result['recall']:.4f}")
    print(f"F1 Score: {result['f1']:.4f}")
    print("Report saved to:", output)


if __name__ == "__main__":
    main()
