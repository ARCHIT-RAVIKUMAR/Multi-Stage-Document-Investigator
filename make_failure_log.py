"""Builds FAILURE_ANALYSIS.md from real run data. Usage: python make_failure_log.py [runs_dir]"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
base = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "runs")
key = {k["id"]: k for k in json.loads((ROOT / "answer_key.json").read_text())["contradictions"]}
scores = json.loads((ROOT / "results" / f"scores_{base.name}.json").read_text())
summary = (ROOT / "results" / f"summary_{base.name}.md").read_text()
norm = lambda s: re.sub(r"\s+", " ", s.lower())

def diagnose(run, issue):
    facts = json.loads((base / run / "stage1_facts.json").read_text())["facts"]
    ftxt = [norm(f["claim"] + " " + f.get("quote", "")) for f in facts]
    kind = issue.split()[0].rstrip(":")
    if kind == "MISSED_CONTRADICTION":
        k = key[issue.split()[1]]
        vals = k["values"]
        absent = [v for v in vals if not any(v in t for t in ftxt)]
        merged = [t for t in ftxt if sum(v in t for v in vals) > 1]
        if absent and k["id"] != "C7":
            return ("bad extraction", f"Stage 1 never extracted a fact containing {absent}, so stage 2 could not have seen the conflict.")
        if merged:
            return ("merged conflicting facts", "Stage 1 put both conflicting values into one fact, hiding the disagreement from stage 2.")
        return ("missed contradiction", "Both sides were extracted as separate facts, but stage 2 did not flag them.")
    if kind == "FABRICATED_QUOTE":
        return ("bad extraction (hallucinated fact)", "Stage 1 produced a quote that is not in the source document; later stages inherit it.")
    if kind in ("OVERREACH", "PICKED_SIDE"):
        return ("final-stage overreach", "Stage 3 stated as established something the document leaves open or contradicts.")
    if kind == "DROPPED_CONFLICT":
        return ("dropped conflict", "Stage 2 flagged it but stage 3 left it out of the unresolved list.")
    if kind == "PHANTOM_CITATION":
        return ("phantom citation", "Stage 3 cited a fact id that stage 1 never produced.")
    return ("pipeline failure", "A stage returned invalid JSON or errored; see ERROR.txt / *_raw.txt.")

# collect issues, prefer variety of categories and different runs
seen, picked = set(), []
for s in scores:
    for i in s["issues"]:
        cat, why = diagnose(s["run"], i)
        if (cat, i.split()[1] if len(i.split()) > 1 else "") in seen: continue
        seen.add((cat, i.split()[1] if len(i.split()) > 1 else ""))
        picked.append((s["run"], i, cat, why))
cats_first = sorted(picked, key=lambda p: p[2])
chosen, used = [], set()
for p in cats_first:
    if p[2] not in used: chosen.append(p); used.add(p[2])
for p in picked:
    if p not in chosen: chosen.append(p)

out = ["# Failure Analysis Log", "", "Generated from the actual run data by `make_failure_log.py`.", "",
       "## Temperature summary", summary, "", f"Total flagged issues across all runs: {sum(len(s['issues']) for s in scores)}", ""]
if len(chosen) < 3:
    out += [f"**Only {len(chosen)} distinct failure(s) were found in these runs**, fewer than the 3 the task asks for. "
            "Run more times (`--runs 10`) or at higher temperatures rather than padding this log.", ""]
for n, (run, issue, cat, why) in enumerate(chosen[:6], 1):
    out += [f"## Failure {n}: {cat}",
            f"- **Run:** `{base.name}/{run}`", f"- **Detected issue:** `{issue}`",
            f"- **Where it started:** {why}",
            f"- **Evidence:** `{base.name}/{run}/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`", ""]
(ROOT / "FAILURE_ANALYSIS.md").write_text("\n".join(out))
print(f"wrote FAILURE_ANALYSIS.md with {min(len(chosen),6)} entries")
