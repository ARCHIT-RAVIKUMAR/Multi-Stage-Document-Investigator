"""Compact view of one run so you can verify a flagged failure. Usage: python show_run.py runs/temp_0.7/run_3"""
import json, sys
from pathlib import Path
run = Path(sys.argv[1])
ld = lambda n: json.loads((run / f"{n}.json").read_text(encoding="utf-8"))
facts = [f for f in ld("stage1_facts")["facts"] if isinstance(f, dict)]
print(f"== STAGE 1: {len(facts)} facts")
for f in facts: print(f'  {f.get("id")}: {f.get("claim")}')
print("\n== STAGE 2: contradictions flagged")
for c in ld("stage2_contradictions")["contradictions"]:
    if isinstance(c, dict): print(f'  {c.get("id")} {c.get("fact_ids")}: {c.get("description")}')
fin = ld("stage3_final")
print("\n== STAGE 3: established findings (should avoid anything in conflict)")
for e in fin.get("established_findings", []): print(f'  - {e.get("text")}  {e.get("fact_ids")}')
print("\n== STAGE 3: unresolved conflicts listed:", len(fin.get("unresolved_conflicts", [])))
print("root_cause_determined:", fin.get("root_cause_determined"))
print("conclusion:", fin.get("conclusion"))
