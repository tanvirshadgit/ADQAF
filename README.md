# ADQAF — Autonomous Data Quality Assurance Framework

[![ADQAF Automated Tests](https://github.com/tanvirshadgit/ADQAF/actions/workflows/tests.yml/badge.svg)](https://github.com/tanvirshadgit/ADQAF/actions/workflows/tests.yml)

[![Release](https://img.shields.io/github/v/release/tanvirshadgit/ADQAF)](https://github.com/tanvirshadgit/ADQAF/releases/tag/v1.0.0)

## Portfolio Overview

ADQAF is a Python-based research and engineering prototype
for quality assurance of YOLO-format object detection datasets.

It combines annotation validation, automated quality gates,
golden-set evaluation, and individual annotator performance
scorecards in a reproducible testing workflow.

**Current release:** v1.0.0

**Verification:** 54 passing unit tests and successful GitHub Actions CI.

**Technology:** Python 3, standard library, GitHub Actions, HTML, JSON, CSV.

**Project status:** Functional prototype; not production-certified.

### Engineering Highlights

- Automated YOLO annotation integrity checks
- Severity-based dataset quality decisions
- Class-aware maximum-cardinality bounding-box matching
- Precision, Recall, F1, TP, FP and FN evaluation
- Configurable annotator quality thresholds
- JSON/CSV reporting and HTML dashboard
- Automated regression testing through GitHub Actions

### Official Release

[ADQAF v1.0.0 — Initial Stable Release](https://github.com/tanvirshadgit/ADQAF/releases/tag/v1.0.0)

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

YOLO Dataset → Validator → Validation Reports → Quality Gate → HTML Dashboard

Ground-Truth Labels + Annotator Labels → Golden-Set Evaluation → Precision / Recall / F1 → Annotator Performance Scorecard → JSON Scorecard

## Requirements

- Python 3
- Git
- No external Python packages required

## Installation and Quick Start

Clone the repository:

    git clone https://github.com/tanvirshadgit/ADQAF.git
    cd ADQAF

Run the automated test suite:

    python3 -m unittest discover -v

Run dataset validation (replace the example path with your local YOLO dataset):

    python3 validator.py --dataset datasets/my_dataset --classes 80 --output reports/my_audit

Generate a quality-gate decision:

    python3 quality_gate.py --report reports/my_audit/quality_report.json --output reports/my_audit/quality_gate.json

The example dataset is not included in the repository. Provide your own dataset using the structure below.

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

Latest verified result: 54 unit tests passed locally, with successful GitHub Actions CI for commit 1de969d (v1.0.0).

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
- Class-aware, maximum-cardinality bipartite one-to-one matching
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

- Maximum-cardinality matching maximizes valid one-to-one matches, but does not guarantee maximum total IoU
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


## Verified Scorecard Demo Results

The local two-file golden-set demonstration produced:

| Metric | Result |
|---|---:|
| Files evaluated | 2 |
| True Positives (TP) | 1 |
| False Positives (FP) | 1 |
| False Negatives (FN) | 1 |
| Precision | 0.5000 |
| Recall | 0.5000 |
| F1 Score | 0.5000 |
| Quality Status | FAIL |

The FAIL status is the expected quality-gate classification for this demonstration, not a software test failure.

These results demonstrate metric calculation and threshold-based classification. They are not a benchmark of ADQAF accuracy or production performance.

The demo dataset is local and is not included in the public repository.

## Annotator Performance Scorecard

ADQAF evaluates individual annotators against verified
YOLO ground-truth annotations.

### Features

- Annotator ID and files evaluated
- TP, FP, FN, Precision, Recall and F1 Score
- Configurable PASS / REVIEW / FAIL thresholds
- JSON report export

### Default Quality Thresholds

| F1 Score | Quality Status |
|---|---|
| 95% or higher | PASS |
| 85% to below 95% | REVIEW |
| Below 85% | FAIL |

These thresholds are configurable project defaults,
not universal industry standards.

### Command-Line Usage

Run the following command from the project directory:

    python3 scorecard_cli.py --annotator-id annotator_001 --ground-truth datasets/golden_set_demo/ground_truth --annotations datasets/golden_set_demo/annotator --iou 0.5 --pass-threshold 0.95 --review-threshold 0.85 --output reports/scorecard/annotator_001.json

The demo dataset must exist locally before running this example.

### Limitations

- Quality status is based on F1 Score only.
- Ground-truth correctness is assumed.
- Files evaluated counts annotation files, not verified images.
- Thresholds should be calibrated to project requirements.
