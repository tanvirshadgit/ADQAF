"""Annotator Performance Scorecard for ADQAF."""


def build_scorecard(
    annotator_id,
    evaluation,
    pass_threshold=0.95,
    review_threshold=0.85
):
    """Build an annotator scorecard from evaluation metrics."""

    if not isinstance(annotator_id, str) or not annotator_id.strip():
        raise ValueError("Annotator ID must be a non-empty string")

    required = (
        "tp", "fp", "fn",
        "precision", "recall", "f1"
    )

    for key in required:
        if key not in evaluation:
            raise ValueError(f"Missing evaluation metric: {key}")

    return {
        "annotator_id": annotator_id,
        "files_evaluated": evaluation.get(
            "files_evaluated",
            len(evaluation.get("per_file", []))
        ),
        "tp": evaluation["tp"],
        "fp": evaluation["fp"],
        "fn": evaluation["fn"],
        "precision": evaluation["precision"],
        "recall": evaluation["recall"],
        "f1": evaluation["f1"],
        "quality_status": calculate_quality_status(
            evaluation["f1"],
            pass_threshold=pass_threshold,
            review_threshold=review_threshold
        ),
    }


def calculate_quality_status(
    f1_score,
    pass_threshold=0.95,
    review_threshold=0.85
):
    """Calculate annotator quality status from F1 score."""

    import math

    values = (f1_score, pass_threshold, review_threshold)

    for value in values:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError(
                "F1 score and thresholds must be finite numbers between 0 and 1"
            )

    if review_threshold > pass_threshold:
        raise ValueError(
            "Review threshold cannot exceed pass threshold"
        )

    if f1_score >= pass_threshold:
        return "PASS"

    if f1_score >= review_threshold:
        return "REVIEW"

    return "FAIL"


def save_scorecard(scorecard, output_path):
    """Save annotator performance scorecard as JSON."""

    import json
    from pathlib import Path

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        json.dumps(scorecard, indent=2),
        encoding="utf-8"
    )

    return output_path
