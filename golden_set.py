"""Golden-set evaluation utilities for YOLO object detection."""

import math


def calculate_iou(box_a, box_b):
    """Calculate IoU for two normalized YOLO (x, y, w, h) boxes."""

    def to_corners(box):
        x, y, w, h = box

        if not all(math.isfinite(v) for v in box):
            raise ValueError("Box coordinates must be finite")

        if w <= 0 or h <= 0:
            raise ValueError("Box width and height must be positive")

        return (
            x - w / 2,
            y - h / 2,
            x + w / 2,
            y + h / 2,
        )

    ax1, ay1, ax2, ay2 = to_corners(box_a)
    bx1, by1, bx2, by2 = to_corners(box_b)

    intersection_width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    intersection_height = max(0.0, min(ay2, by2) - max(ay1, by1))

    intersection = intersection_width * intersection_height

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)

    union = area_a + area_b - intersection

    return intersection / union


def match_annotations(ground_truth, annotations, iou_threshold=0.5):
    """Match (class_id, x, y, w, h) annotations one-to-one."""

    if not 0 < iou_threshold <= 1:
        raise ValueError("IoU threshold must be between 0 and 1")

    candidates = []

    for gt_index, gt in enumerate(ground_truth):
        for ann_index, ann in enumerate(annotations):
            if gt[0] != ann[0]:
                continue

            iou = calculate_iou(gt[1:], ann[1:])

            if iou >= iou_threshold:
                candidates.append((iou, gt_index, ann_index))

    candidates.sort(reverse=True)

    matched_gt = set()
    matched_ann = set()

    for iou, gt_index, ann_index in candidates:
        if gt_index in matched_gt or ann_index in matched_ann:
            continue

        matched_gt.add(gt_index)
        matched_ann.add(ann_index)

    tp = len(matched_gt)
    fp = len(annotations) - tp
    fn = len(ground_truth) - tp

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def save_evaluation_report(result, output_path):
    """Save golden-set evaluation metrics as JSON."""
    import json
    from pathlib import Path

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    return output_path


def read_yolo_annotations(file_path):
    """Read and validate YOLO bounding-box annotations."""
    from pathlib import Path

    path = Path(file_path)
    annotations = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        if not line.strip():
            continue

        fields = line.split()

        if len(fields) != 5:
            raise ValueError(
                f"{path}:{line_number}: Expected 5 fields"
            )

        try:
            values = [float(value) for value in fields]
        except ValueError as exc:
            raise ValueError(
                f"{path}:{line_number}: Non-numeric annotation"
            ) from exc

        if not all(math.isfinite(value) for value in values):
            raise ValueError(
                f"{path}:{line_number}: Non-finite annotation"
            )

        class_id, x, y, w, h = values

        if class_id < 0 or not class_id.is_integer():
            raise ValueError(
                f"{path}:{line_number}: Invalid class ID"
            )

        if (
            not all(0 <= value <= 1 for value in (x, y, w, h))
            or w <= 0
            or h <= 0
            or x - w / 2 < -1e-6
            or y - h / 2 < -1e-6
            or x + w / 2 > 1 + 1e-6
            or y + h / 2 > 1 + 1e-6
        ):
            raise ValueError(
                f"{path}:{line_number}: Invalid bounding box"
            )

        annotations.append((int(class_id), x, y, w, h))

    return annotations


def evaluate_annotation_files(
    ground_truth_path,
    annotation_path,
    iou_threshold=0.5
):
    """Evaluate an annotator's YOLO file against a golden-set file."""

    ground_truth = read_yolo_annotations(ground_truth_path)
    annotations = read_yolo_annotations(annotation_path)

    result = match_annotations(
        ground_truth,
        annotations,
        iou_threshold=iou_threshold
    )

    return {
        "evaluation_type": "golden_set",
        "ground_truth_file": str(ground_truth_path),
        "annotation_file": str(annotation_path),
        "iou_threshold": iou_threshold,
        "ground_truth_boxes": len(ground_truth),
        "annotation_boxes": len(annotations),
        **result
    }


def evaluate_annotation_directories(
    ground_truth_dir,
    annotation_dir,
    iou_threshold=0.5
):
    """Evaluate matching YOLO annotation files across directories."""
    from pathlib import Path

    ground_truth_dir = Path(ground_truth_dir)
    annotation_dir = Path(annotation_dir)

    if not ground_truth_dir.is_dir() or not annotation_dir.is_dir():
        raise ValueError("Both annotation directories must exist")

    if not 0 < iou_threshold <= 1:
        raise ValueError("IoU threshold must be between 0 and 1")

    def collect_files(directory):
        return {
            path.relative_to(directory).as_posix(): path
            for path in directory.rglob("*")
            if path.is_file() and path.suffix.lower() == ".txt"
        }

    gt_files = collect_files(ground_truth_dir)
    ann_files = collect_files(annotation_dir)

    filenames = sorted(set(gt_files) | set(ann_files))

    if not filenames:
        raise ValueError("No annotation files found")

    missing_ground_truth = sorted(set(ann_files) - set(gt_files))

    if missing_ground_truth:
        raise ValueError(
            "Missing ground-truth files: "
            + ", ".join(missing_ground_truth)
        )

    totals = {"tp": 0, "fp": 0, "fn": 0}
    per_file = []

    for filename in filenames:
        gt = (
            read_yolo_annotations(gt_files[filename])
            if filename in gt_files else []
        )
        ann = (
            read_yolo_annotations(ann_files[filename])
            if filename in ann_files else []
        )

        result = match_annotations(gt, ann, iou_threshold)

        for metric in totals:
            totals[metric] += result[metric]

        per_file.append({
            "file": filename,
            "ground_truth_file_present": filename in gt_files,
            "annotation_file_present": filename in ann_files,
            **result
        })

    tp, fp, fn = totals["tp"], totals["fp"], totals["fn"]

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "evaluation_type": "golden_set_dataset",
        "iou_threshold": iou_threshold,
        "files_evaluated": len(filenames),
        **totals,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "per_file": per_file
    }
