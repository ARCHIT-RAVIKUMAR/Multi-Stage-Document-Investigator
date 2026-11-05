#!/usr/bin/env python3
"""3-stage document investigator. Usage:
  python pipeline.py --temps 0 0.7 1.0 --runs 3 [--model MODEL] [--mock]
Requires: pip install anthropic ; export ANTHROPIC_API_KEY=...
"""
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).parent
DOC = (ROOT / "source_document.md").read_text()
P = {k: (ROOT / f"prompts/{v}.txt").read_text() for k, v in
     {"s1": "stage1_extract", "s2": "stage2_contradictions", "s3": "stage3_reasoning"}.items()}

def parse_json(text):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M).strip()
    try: return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.S)
        if not m: raise
        return json.loads(m.group(0))

def mock_llm(stage, temp):
    q = lambda s: s  # quotes below are verbatim from source_document.md
    if stage == "s1":
        facts = [
          {"id":"F1","claim":"Power lost at 02:14","category":"time","sections":["1"],"quote":"lost utility power at 02:14 local time"},
          {"id":"F2","claim":"Utility feed alarm at 02:41","category":"time","sections":["3"],"quote":"02:41 - Monitoring raised a utility feed lost alarm for Building 2."},
          {"id":"F3","claim":"Cause triggered by a storm","category":"cause","sections":["1"],"quote":"The utility fault was triggered by a storm."},
          {"id":"F4","claim":"Clear skies that night","category":"cause","sections":["7"],"quote":"recorded clear skies, no precipitation"},
          {"id":"F5","claim":"Root cause under investigation","category":"cause","sections":["1"],"quote":"The full root cause is still under investigation."}]
        if temp >= 1.0:
            facts.append({"id":"F6","claim":"Customer data was lost","category":"other","sections":["1"],"quote":"Some customer data was permanently lost."})
        return {"facts": facts}
    if stage == "s2":
        return {"contradictions":[
          {"id":"X1","fact_ids":["F1","F2"],"topic":"start time","description":"F1 says 02:14 but F2 says 02:41","confidence":"high"},
          {"id":"X2","fact_ids":["F3","F4"],"topic":"cause","description":"F3 says storm but F4 says clear weather","confidence":"medium"}]}
    return {"established_findings":[{"text":"Root cause is under investigation.","fact_ids":["F5"]}],
            "unresolved_conflicts":[{"contradiction_id":"X1","summary":"start time 02:14 vs 02:41","what_would_resolve_it":"raw logs"}],
            "root_cause_determined": temp >= 1.0, "root_cause_statement":"unknown",
            "not_supported_by_evidence":["data loss"],"overall_confidence":"low","conclusion":"mock"}

def real_llm(system, user, temp, model):
    import anthropic
    c = anthropic.Anthropic()
    r = c.messages.create(model=model, max_tokens=4000, temperature=temp, system=system,
                          messages=[{"role": "user", "content": user}])
    return "".join(b.text for b in r.content if b.type == "text")

def run_stage(stage, user, temp, model, mock, out: Path, name):
    if mock:
        raw = json.dumps(mock_llm(stage, temp))
    else:
        raw = real_llm(P[stage], user, temp, model)
    (out / f"{name}_raw.txt").write_text(raw)
    try:
        data = parse_json(raw)
    except Exception as e:
        # one retry with a nudge, logged in the raw file
        if mock: raise
        raw2 = real_llm(P[stage] + "\nYour previous reply was not valid JSON. Return ONLY JSON.", user, temp, model)
        (out / f"{name}_raw_retry.txt").write_text(raw2)
        data = parse_json(raw2)
    (out / f"{name}.json").write_text(json.dumps(data, indent=2))
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--temps", nargs="+", type=float, default=[0.0, 0.7, 1.0])
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--mock", action="store_true", help="offline plumbing test; NOT real model output")
    a = ap.parse_args()
    base = ROOT / ("runs_mock" if a.mock else "runs")
    for t in a.temps:
        for i in range(1, a.runs + 1):
            out = base / f"temp_{t}" / f"run_{i}"; out.mkdir(parents=True, exist_ok=True)
            try:
                f = run_stage("s1", DOC, t, a.model, a.mock, out, "stage1_facts")
                # Stage 2 sees ONLY the facts JSON (no raw document)
                c = run_stage("s2", json.dumps(f, indent=1), t, a.model, a.mock, out, "stage2_contradictions")
                # Stage 3 sees ONLY facts + contradictions
                run_stage("s3", json.dumps({"facts": f, "contradictions": c}, indent=1), t, a.model, a.mock, out, "stage3_final")
                print(f"ok   temp={t} run={i}")
            except Exception as e:
                (out / "ERROR.txt").write_text(repr(e)); print(f"FAIL temp={t} run={i}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
