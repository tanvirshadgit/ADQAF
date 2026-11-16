import argparse
import csv
import json
from collections import Counter
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def validate_dataset(root: Path, class_count: int):
    images_dir, labels_dir = root / 'images', root / 'labels'
    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise ValueError('Dataset must contain images/ and labels/ directories')
    if class_count < 1:
        raise ValueError('class_count must be positive')
    images = sorted(p for p in images_dir.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    issues = []
    checked = 0
    for image in images:
        checked += 1
        relative = image.relative_to(images_dir).with_suffix('.txt')
        label = labels_dir / relative
        if not label.exists():
            issues.append(dict(image=str(image.relative_to(root)), line='', code='MISSING_LABEL', detail='No annotation file; may be an intentional negative sample'))
            continue
        lines = label.read_text(encoding='utf-8-sig').splitlines()
        if not any(line.strip() for line in lines):
            issues.append(dict(image=str(image.relative_to(root)), line='', code='EMPTY_LABEL', detail='Empty label; may be an intentional negative sample'))
        seen = set()
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            fields = line.split()
            base = dict(image=str(image.relative_to(root)), line=number)
            if len(fields) != 5:
                issues.append(dict(**base, code='INVALID_FORMAT', detail=f'Expected 5 fields, got {len(fields)}'))
                continue
            try:
                cls_float = float(fields[0]); vals = [float(v) for v in fields[1:]]
            except ValueError:
                issues.append(dict(**base, code='NON_NUMERIC', detail='Class or coordinates are not numeric'))
                continue
            import math
            if not all(math.isfinite(v) for v in [cls_float] + vals):
                issues.append(dict(**base, code='NON_FINITE', detail='NaN/Infinity is invalid'))
                continue
            if not cls_float.is_integer() or not 0 <= cls_float < class_count:
                issues.append(dict(**base, code='INVALID_CLASS', detail=f'Class must be an integer in [0, {class_count-1}]'))
            x, y, w, h = vals
            if not all(0 <= v <= 1 for v in vals) or w <= 0 or h <= 0 or x-w/2 < -1e-6 or y-h/2 < -1e-6 or x+w/2 > 1+1e-6 or y+h/2 > 1+1e-6:
                issues.append(dict(**base, code='INVALID_BOX', detail='Bounding box must have positive area and stay within image bounds'))
            signature = tuple(fields)
            if signature in seen:
                issues.append(dict(**base, code='DUPLICATE_BOX', detail='Exact duplicate annotation'))
            seen.add(signature)
    for label in sorted(labels_dir.rglob('*.txt')):
        relative = label.relative_to(labels_dir)
        if not any((images_dir / relative.with_suffix(ext)).exists() for ext in IMAGE_EXTENSIONS):
            issues.append(dict(image=str(label.relative_to(root)), line='', code='ORPHAN_LABEL', detail='Label has no matching image'))
    counts = dict(sorted(Counter(i['code'] for i in issues).items()))
    return {'images_checked': checked, 'issues_found': len(issues), 'issue_counts': counts, 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description='Validate YOLO detection annotations')
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--classes', type=int, required=True)
    parser.add_argument('--output', type=Path, default=Path('reports'))
    args = parser.parse_args()
    report = validate_dataset(args.dataset, args.classes)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'quality_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    with (args.output / 'issues.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['image', 'line', 'code', 'detail'])
        writer.writeheader(); writer.writerows(report['issues'])
    print(f"Checked {report['images_checked']} images; found {report['issues_found']} issues")
    print('Issue counts:', report['issue_counts'])
    print('Reports saved to', args.output)


if __name__ == '__main__':
    main()
