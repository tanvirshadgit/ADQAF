# ADQAF: Engineering an Automated Quality Assurance Framework for Computer Vision Datasets

**Project:** Autonomous Data Quality Assurance Framework (ADQAF)

**Type:** Independent Software Engineering and Research Prototype

**Domain:** Computer Vision, AI Data Quality Engineering

**Technology:** Python 3, GitHub Actions, JSON, CSV, HTML

**Repository:** https://github.com/tanvirshadgit/ADQAF

**Release:** v1.0.0

## 1. Problem Statement

Object detection systems rely on accurately formatted and consistently annotated training data.
Invalid bounding boxes, incorrect class identifiers, missing annotation files, and inconsistent
object labels can introduce quality risks into computer vision datasets.

Manual annotation quality assurance can be time-consuming, difficult to standardize,
and challenging to reproduce across annotation teams.

ADQAF explores how rule-based validation and reference-based evaluation can
support more consistent and measurable annotation quality assurance.

## 2. Project Objectives

- Automate structural validation of YOLO-format annotations.
- Detect dataset integrity and annotation formatting issues.
- Apply severity-based dataset quality decisions.
- Compare annotations against reference ground-truth labels.
- Measure annotator performance using standard detection metrics.
- Generate reproducible reports for quality review.
- Verify implementation behavior through automated unit tests.

## 3. Solution Overview

ADQAF implements two complementary quality-assurance workflows:

**Dataset Validation:** YOLO Dataset -> Validator -> Validation Reports -> Quality Gate -> HTML Dashboard.

**Annotator Evaluation:** Ground Truth + Annotator Labels -> Golden-Set Evaluation -> Performance Scorecard -> JSON Report.

The framework is implemented using the Python standard library.
It is a functional engineering prototype, not a production-certified system.

## 4. Technical Implementation

### 4.1 YOLO Dataset Validator

The validator performs structural and numerical checks on YOLO-format annotations.

Implemented checks include:

- Invalid annotation structure and field counts.
- Invalid or out-of-range class identifiers.
- Non-numeric and non-finite bounding-box coordinates.
- Invalid normalized bounding-box dimensions and boundaries.
- Exact numeric duplicate annotations.
- Missing, empty, and orphan annotation files.
- Empty dataset detection and configurable missing-label handling.

Numerical boundary tolerance helps reduce false-positive findings caused by floating-point rounding.

### 4.2 Automated Quality Gate

The quality gate interprets validation findings using severity-based rules.
It generates PASS, REVIEW, or FAIL decisions to support dataset review.

A passing decision does not guarantee semantic annotation correctness.

### 4.3 Golden-Set Evaluation

ADQAF compares annotator bounding boxes with reference annotations using
Intersection over Union (IoU) and class-aware one-to-one matching.

The matching algorithm uses maximum-cardinality bipartite matching
to maximize the number of valid matches under the configured IoU threshold.

Evaluation outputs include true positives, false positives, false negatives,
precision, recall, and F1 score.

### 4.4 Annotator Performance Scorecard

The scorecard summarizes evaluation metrics for an individual annotator.
It supports configurable F1-based quality thresholds:

- PASS: F1 >= 0.95
- REVIEW: 0.85 <= F1 < 0.95
- FAIL: F1 < 0.85

These thresholds are project defaults, not universal industry standards.

### 4.5 Reporting and Dashboard

The framework generates JSON and CSV validation reports,
JSON annotator scorecards, and an HTML quality dashboard.

## 5. Engineering Design Decisions

### Class-Aware Matching

Bounding boxes with different class identifiers are not considered valid matches,
even when their spatial coordinates overlap.

### Maximum-Cardinality Matching

Maximum-cardinality matching avoids some order-dependent undercounting
problems associated with greedy one-to-one matching.
It does not necessarily maximize the total IoU of matched pairs.

### Configurable Quality Policies

Missing-label handling, IoU thresholds, and annotator score thresholds
can be adjusted according to project requirements.

### Dependency-Minimal Implementation

The framework uses the Python standard library to simplify
installation, testing, and reproducibility.

## 6. Testing and Verification

ADQAF includes automated unit tests covering dataset validation,
golden-set evaluation, quality decisions, and scorecard functionality.

- 54 unit tests passed locally.
- GitHub Actions CI successfully executed automated tests.
- Public demonstration annotation files are included in the repository.
- The framework can be tested without external Python dependencies.

Testing confirms the covered behaviors but does not establish
production readiness or comprehensive integration coverage.

## 7. Verified Demonstration Results

A two-file synthetic YOLO annotation example was evaluated
using the Golden-Set Evaluation and Scorecard CLI.

| Metric | Result |
|---|---:|
| Files evaluated | 2 |
| True Positives | 1 |
| False Positives | 1 |
| False Negatives | 1 |
| Precision | 0.5000 |
| Recall | 0.5000 |
| F1 Score | 0.5000 |
| Quality Status | FAIL |

The FAIL classification is expected because the demonstration
F1 score falls below the configured REVIEW threshold.

This demonstrates functional behavior, not model accuracy improvement.

Reproducible example:

    python3 scorecard_cli.py --annotator-id demo_annotator --ground-truth examples/golden_set_demo/ground_truth --annotations examples/golden_set_demo/annotator --iou 0.5 --output reports/scorecard/public_demo.json

## 8. Limitations and Future Development

Current limitations:

- Supports YOLO-format object detection annotations.
- Ground-truth annotations are assumed to be correct.
- Structural validation cannot establish semantic correctness.
- Quality status uses F1-based thresholds.
- Image-content integrity is not independently verified.
- Broader integration and production testing remain future work.

Potential future improvements:

- Risk-based annotation QA sampling.
- IoU-based near-duplicate detection.
- Image integrity verification.
- Expanded automated integration testing.
- More flexible dashboard configuration.

## 9. Research Relevance and Conclusion

ADQAF connects practical annotation quality engineering
with data-centric computer vision research.

A related independent research manuscript examines
bounding-box annotation noise and object detection performance:

Impact of Bounding Box Annotation Noise on Object Detection Performance

https://zenodo.org/records/24224386

The research and ADQAF are separate projects with related interests
in annotation quality and reliable computer vision datasets.

ADQAF demonstrates a tested, reproducible approach to
dataset validation, reference-based evaluation,
annotator performance measurement, and QA reporting.
