import json
import html
from pathlib import Path

folder = Path("reports/coco128_tolerance_test")

audit = json.loads(
    (folder / "quality_report.json").read_text()
)
gate = json.loads(
    (folder / "quality_gate.json").read_text()
)

def safe(value):
    return html.escape(str(value))

rows = ""
for finding in gate["findings"]:
    rows += (
        "<tr>"
        f"<td>{safe(finding.get('image', ''))}</td>"
        f"<td>{safe(finding.get('code', ''))}</td>"
        f"<td>{safe(finding.get('severity', ''))}</td>"
        f"<td>{safe(finding.get('review_status', ''))}</td>"
        "</tr>"
    )

bars = ""
maximum = max(audit["issue_counts"].values(), default=1)

for code, count in audit["issue_counts"].items():
    width = count / maximum * 100
    bars += (
        f"<p>{safe(code)} — {count}</p>"
        f'<div class="track"><div class="bar" '
        f'style="width:{width:.1f}%"></div></div>'
    )

decision = gate["decision"]
decision_color = {
    "PASS": "#15803d",
    "REVIEW": "#b45309",
    "FAIL": "#b91c1c",
}.get(decision, "#374151")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADQAF Quality Dashboard</title>
<style>
body {{
  font-family: Arial, sans-serif;
  background: #f4f6fa;
  color: #172033;
  margin: 0;
  padding: 32px;
}}
main {{ max-width: 1050px; margin: auto; }}
h1 {{ margin-bottom: 6px; }}
.subtitle {{ color: #64748b; margin-bottom: 30px; }}
.cards {{
  display: grid;
  grid-template-columns: repeat(auto-fit,minmax(180px,1fr));
  gap: 16px;
}}
.card, section {{
  background: white;
  padding: 22px;
  border-radius: 12px;
  box-shadow: 0 2px 10px #0000000b;
}}
.card span {{ color: #64748b; }}
.card strong {{ display:block;font-size:30px;margin-top:10px; }}
section {{ margin-top: 22px; }}
.track {{
  height: 14px;
  background: #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}}
.bar {{ height:100%;background:#2563eb; }}
table {{ width:100%;border-collapse:collapse; }}
th,td {{
  text-align:left;
  padding:12px;
  border-bottom:1px solid #e2e8f0;
}}
th {{ background:#f8fafc; }}
.table-wrap {{ overflow-x:auto; }}
</style>
</head>
<body>
<main>
<h1>ADQAF Quality Dashboard</h1>
<p class="subtitle">Autonomous Data Quality Assurance Framework</p>

<div class="cards">
  <div class="card"><span>Images checked</span>
    <strong>{audit["images_checked"]}</strong></div>
  <div class="card"><span>Total findings</span>
    <strong>{gate["total_findings"]}</strong></div>
  <div class="card"><span>Warnings</span>
    <strong>{gate["severity_counts"].get("WARNING",0)}</strong></div>
  <div class="card"><span>Errors</span>
    <strong>{gate["severity_counts"].get("ERROR",0)}</strong></div>
  <div class="card"><span>Quality Gate</span>
    <strong style="color:{decision_color}">{safe(decision)}</strong></div>
</div>

<section>
<h2>Issue Distribution</h2>
{bars}
</section>

<section>
<h2>Detailed Findings</h2>
<div class="table-wrap">
<table>
<thead>
<tr><th>File</th><th>Issue</th><th>Severity</th><th>Review Status</th></tr>
</thead>
<tbody>{rows}</tbody>
</table>
</div>
</section>

<p class="subtitle">Generated from ADQAF audit reports.</p>
</main>
</body>
</html>"""

output = folder / "dashboard.html"
output.write_text(page, encoding="utf-8")

print("SUCCESS: Dashboard created")
print("File:", output)
