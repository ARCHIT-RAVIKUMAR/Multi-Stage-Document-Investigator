#!/usr/bin/env python3
"""Scores each run against answer_key.json. Usage: python evaluate.py [runs|runs_mock]
Heuristic checks -> always manually verify flagged runs before writing them up."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).parent
base = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "runs")
KEY = json.loads((ROOT / "answer_key.json").read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"\s+", " ", s.lower()).strip()
DOC = norm((ROOT / "source_document.md").read_text(encoding="utf-8"))


def check_structure(run: Path):
    """Return a message naming the stage and the problem, or None if the shape is usable."""
    for fn, key, need in [("stage1_facts", "facts", "id"), ("stage2_contradictions", "contradictions", None)]:
        d = json.loads((run / f"{fn}.json").read_text(encoding="utf-8"))
        v = d.get(key) if isinstance(d, dict) else None
        if not isinstance(v, list):
            return f"{fn}.json: '{key}' missing or not a list (top level is {type(d).__name__}, keys={list(d)[:5] if isinstance(d, dict) else 'n/a'})"
        bad = [x for x in v if not isinstance(x, dict) and not (isinstance(x, str) and not x.strip())]
        if bad:
            return f"{fn}.json: '{key}' has {len(bad)} non-object item(s), first is {str(bad[0])[:70]!r}"
        if need and any(need not in x for x in v if isinstance(x, dict)):
            return f"{fn}.json: some items have no '{need}' field"
    fin = json.loads((run / "stage3_final.json").read_text(encoding="utf-8"))
    if not isinstance(fin, dict):
        return f"stage3_final.json: top level is {type(fin).__name__}, expected object"
    ef = fin.get("established_findings", [])
    if not isinstance(ef, list) or any(not isinstance(x, dict) or "text" not in x for x in ef):
        return f"stage3_final.json: 'established_findings' items must be objects with 'text' (first: {str(ef[:1])[:70]!r})"
    return None

def _score(run: Path):
    r = {"run": str(run.relative_to(base)), "issues": []}
    try:
        facts = json.loads((run / "stage1_facts.json").read_text(encoding="utf-8"))["facts"]
        cons = json.loads((run / "stage2_contradictions.json").read_text(encoding="utf-8"))["contradictions"]
        fin = json.loads((run / "stage3_final.json").read_text(encoding="utf-8"))
    except Exception as e:
        r["issues"].append(f"PIPELINE_FAILURE: {e}"); r.update(recall=None, fabricated=0); return r
    n_junk = sum(1 for f in facts if not isinstance(f, dict)) + sum(1 for c in cons if not isinstance(c, dict))
    facts = [f for f in facts if isinstance(f, dict)]
    cons = [c for c in cons if isinstance(c, dict)]
    if n_junk: r["issues"].append(f"MALFORMED_ITEMS (ignored, minor): {n_junk} empty entries in stage 1/2 lists")
    byid = {f["id"]: f for f in facts}
    # 1. fabricated quotes (extraction hallucination)
    bad = [f["id"] for f in facts if norm(f.get("quote", "")) not in DOC]
    r["fabricated"] = len(bad)
    for b in bad: r["issues"].append(f"FABRICATED_QUOTE {b}: {byid[b].get('quote')!r}")
    # 2. recall of planted contradictions
    found = set()
    for c in cons:
        txt = norm(c.get("description", "") + " " + c.get("topic", "") + " " +
                   " ".join(byid.get(i, {}).get("claim", "") + " " + byid.get(i, {}).get("quote", "") for i in c.get("fact_ids", [])))
        for k in KEY["contradictions"]:
            if any(all(w in txt for w in g) for g in k["any_of"]): found.add(k["id"])
    missed = [k["id"] for k in KEY["contradictions"] if k["id"] not in found]
    r["recall"] = len(found) / len(KEY["contradictions"]); r["missed"] = missed
    for m in missed: r["issues"].append(f"MISSED_CONTRADICTION {m}")
    # 3. final-stage overreach
    est = " ".join(norm(e["text"]) for e in fin.get("established_findings", []))
    for pat in KEY["forbidden_established_claims"]:
        if re.search(pat, est): r["issues"].append(f"OVERREACH: established claim matches /{pat}/")
    for k in KEY["contradictions"]:
        present = [v for v in k["values"] if v in est]
        if len(k["values"]) > 1 and len(present) == 1: r["issues"].append(f"PICKED_SIDE {k['id']}: only {present[0]!r} stated as established")
    if fin.get("root_cause_determined") is True: r["issues"].append("OVERREACH: root_cause_determined=true (doc says under investigation)")
    ids = {c.get("id") for c in cons}; resolved = {u.get("contradiction_id") for u in fin.get("unresolved_conflicts", [])}
    for i in sorted(ids - resolved): r["issues"].append(f"DROPPED_CONFLICT: {i} flagged in stage 2 but absent from stage 3")
    for e in fin.get("established_findings", []):
        for i in e.get("fact_ids", []):
            if i not in byid: r["issues"].append(f"PHANTOM_CITATION: stage 3 cites unknown fact {i}")
    r["false_positive_candidates"] = len([c for c in cons if not any(
        any(all(w in norm(c.get('description','')+' '+c.get('topic','')) for w in g) for g in k['any_of']) for k in KEY['contradictions'])])
    return r


def score(run: Path):
    try:
        msg = check_structure(run)
        if msg:
            return {"run": str(run.relative_to(base)), "recall": None, "fabricated": 0, "missed": [],
                    "false_positive_candidates": 0, "issues": [f"SCHEMA_VIOLATION: {msg}"]}
        return _score(run)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError) as e:
        return {"run": str(run.relative_to(base)), "recall": None, "fabricated": 0, "missed": [],
                "false_positive_candidates": 0,
                "issues": [f"SCHEMA_VIOLATION: a stage returned the wrong structure ({type(e).__name__}: {e})"]}

rows = [score(p) for p in sorted(base.glob("temp_*/run_*")) if p.is_dir()]
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / f"scores_{base.name}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
by = {}
for r in rows: by.setdefault(Path(r["run"]).parts[0], []).append(r)
lines = ["| temp | runs | mean recall | fabricated quotes | overreach/pick-side/dropped | false-positive candidates |", "|---|---|---|---|---|---|"]
for t, rs in by.items():
    n = len(rs); ok = [x["recall"] for x in rs if x.get("recall") is not None]; rec = (sum(ok) / len(ok)) if ok else None
    fab = sum(x.get("fabricated", 0) for x in rs)
    ov = sum(1 for x in rs for i in x["issues"] if i.split()[0].rstrip(":").split("_")[0] in ("OVERREACH", "PICKED", "DROPPED", "PHANTOM", "SCHEMA", "PIPELINE"))
    fp = sum(x.get("false_positive_candidates", 0) for x in rs)
    lines.append(f"| {t} | {n} | {"n/a" if rec is None else format(rec, ".2f")} | {fab} | {ov} | {fp} |")
md = "\n".join(lines)
(ROOT / "results" / f"summary_{base.name}.md").write_text(md + "\n", encoding="utf-8")
print(md)
for r in rows:
    if r["issues"]: print("\n" + r["run"]); [print("  -", i) for i in r["issues"]]
