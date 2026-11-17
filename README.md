# ADQAF — Autonomous Data Quality Assurance Framework

[![ADQAF Automated Tests](https://github.com/tanvirshadgit/ADQAF/actions/workflows/tests.yml/badge.svg)](https://github.com/tanvirshadgit/ADQAF/actions/workflows/tests.yml)

A Python-based prototype for automated quality assurance of YOLO object-detection datasets.

ADQAF demonstrates annotation validation, dataset integrity checks, automated quality gates, regression testing, and HTML reporting.

**Status:** Functional research and engineering prototype. Not production-certified.

## Features

- YOLO bounding-box validation
- Invalid class ID detection
- Non-numeric and non-finite value detection
- Invalid annotation format detection
- Exact numeric duplicate annotation detection (including equivalent decimal formatting)
- Missing and empty label detection
- Orphan label detection with cross-platform image extension handling
- Empty dataset detection
- Numerical boundary tolerance
- Severity classification
- Automated PASS / REVIEW / FAIL decisions
- JSON and CSV reports
- HTML quality dashboard
- Automated unit tests

## Architecture

YOLO Dataset → Validator → JSON/CSV Report → Quality Gate → HTML Dashboard

## Requirements

Python 3. No external Python packages required.

## Dataset Structure

Images and labels must use matching relative paths under their respective directories.

Example dataset layout:

    datasets/
      my_dataset/
        images/
          train/
            image001.jpg
            image002.jpg
        labels/
          train/
            image001.txt
            image002.txt

Each image and its annotation file should share the same relative path and filename stem.

YOLO annotation format:

class_id x_center y_center width height

Coordinates are normalized to 0–1.

## Run Validation

    python3 validator.py --dataset datasets/coco128 --classes 80 --output reports/coco128_tolerance_test

## Run Quality Gate

    python3 quality_gate.py --report reports/coco128_tolerance_test/quality_report.json --output reports/coco128_tolerance_test/quality_gate.json

## Generate Dashboard

    python3 dashboard.py

On macOS:

    open reports/coco128_tolerance_test/dashboard.html

The current dashboard generator uses a fixed report directory.


## Quality Dashboard Preview

The dashboard visualizes dataset quality findings,
severity classifications, and quality-gate decisions.

![ADQAF Quality Dashboard](docs/dashboard.png)

## Automated Testing

    python3 -m unittest discover -v

Latest verified result: 17 unit tests passed locally and in GitHub Actions CI.

## COCO128 Audit Results

Images checked: 128.

Initial findings: 46.

After adjusting boundary tolerance from 1e-9 to 1e-6:

- INVALID_BOX: 0
- MISSING_LABEL: 2
- ORPHAN_LABEL: 2
- Total findings: 4

The 42 previously flagged boxes no longer triggered INVALID_BOX findings after the tolerance adjustment. This suggests rounding-related false positives but does not conclusively establish that all 42 were valid.

The remaining findings require dataset-level review.

Quality Gate decision: FAIL.

Warnings: 2. Errors: 2.

## Limitations

- No image-content integrity verification
- No semantic annotation correctness evaluation
- Exact numeric duplicate detection only; IoU-based near-duplicate detection is not implemented
- Missing labels may be intentional negative samples
- Fixed dashboard input directory
- GitHub Actions runs automated unit tests; broader integration and deployment testing are not yet implemented
- A passing quality gate does not guarantee dataset correctness

## Roadmap

- Golden-set evaluation
- IoU-based duplicate detection
- Risk-based QA sampling
- Image integrity checks
- Configurable quality thresholds
- Expand CI coverage with integration tests and automated dataset audits
- Camera–LiDAR synchronization validation


## Golden-Set Evaluation

ADQAF compares YOLO annotations against verified ground-truth labels.

### Features

- Bounding-box IoU calculation
- Class-aware, greedy one-to-one matching
- TP, FP, FN, Precision, Recall and F1 Score
- Dataset-level evaluation
- Missing ground-truth safety checks
- JSON reports and CLI support

### Dataset Structure

    golden_dataset/
      ground_truth/
        image001.txt
        image002.txt
      annotator/
        image001.txt
        image002.txt

### Run Evaluation

    python3 golden_set_cli.py --ground-truth datasets/golden_set_demo/ground_truth --annotations datasets/golden_set_demo/annotator --iou 0.5 --output reports/golden_set/evaluation.json

### Limitations

- Greedy matching does not guarantee globally optimal matching
- Ground-truth correctness is not independently verified
- Image inventory completeness is not checked
- Missing annotator files are treated as empty annotations
- Missing ground-truth files corresponding to annotator files cause an error

## Related Research

Impact of Bounding Box Annotation Noise on Object Detection Performance

https://zenodo.org/records/24224386

## Author

Tanvir Ahmed Khan

Computer Vision | AI Data Quality Assurance | Data Operations

## Missing Label Policy

ADQAF supports configurable handling of images without annotation files.

- `warn` (default): Reports `MISSING_LABEL` for review.
- `allow`: Accepts missing annotation files as intentional negative samples.

Example (default policy):

    python3 validator.py --dataset datasets/coco128 --classes 80 --output reports/audit --missing-label-policy warn

Example (allow negative samples):

    python3 validator.py --dataset datasets/coco128 --classes 80 --output reports/negative_samples --missing-label-policy allow

Use `allow` only when the dataset annotation policy permits missing label files. Empty label files are still reported.
