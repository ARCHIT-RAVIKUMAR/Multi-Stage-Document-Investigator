import json, sys
from pathlib import Path

run = Path(sys.argv[1])
f = json.loads((run / "stage3_final.json").read_text())
facts = {x["id"]: x["claim"] for x in json.loads((run / "stage1_facts.json").read_text())["facts"]}

out = ["# Final Report", f"_Source run: {run}_", "", "## Conclusion", f.get("conclusion", ""), "",
       "## Established findings"]
for e in f.get("established_findings", []):
    out.append(f"- {e['text']} ({', '.join(e.get('fact_ids', []))})")
out += ["", "## Unresolved conflicts"]
for u in f.get("unresolved_conflicts", []):
    out.append(f"- **{u.get('contradiction_id')}**: {u.get('summary')} - would resolve: {u.get('what_would_resolve_it')}")
out += ["", "## Root cause", f"Determined: {f.get('root_cause_determined')}", f.get("root_cause_statement", ""), "",
        "## Not supported by the document"]
out += [f"- {x}" for x in f.get("not_supported_by_evidence", [])]
out += ["", f"Overall confidence: {f.get('overall_confidence')}"]
Path("REPORT.md").write_text("\n".join(out) + "\n")
print("wrote REPORT.md")
