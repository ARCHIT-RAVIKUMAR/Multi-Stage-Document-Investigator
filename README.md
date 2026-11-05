# Document Investigator

Three-stage LLM pipeline that reads a messy incident report, pulls out facts, finds contradictions, and writes a conclusion.

## Stages
1. **Extract** - facts from the raw document (with verbatim quotes)
2. **Contradictions** - gets only the facts JSON, not the document
3. **Reasoning** - gets only facts + contradictions JSON

## Files
- `source_document.md` - the messy document (8 planted contradictions)
- `answer_key.json` - what I planted, used for scoring
- `prompts/` - one prompt per stage
- `pipeline.py` - runs everything at the temperatures you give it
- `evaluate.py` - scores runs against the key
- `make_report.py` - turns a run's stage 3 JSON into `REPORT.md`
- `runs/` - intermediate JSON for every stage / temperature / run
- `FAILURE_ANALYSIS.md` - the failures I found and why

## Planted contradictions
1. Start time: 02:14 vs 02:41
2. Restored: 06:34 vs 08:05
3. Customers affected: 312 vs 213
4. Failover approved by Priya Raman vs Daniel Okafor
5. UPS ran 15 min vs 9 min
6. Generator B fuel: ~11 hours vs 20% (~3 hours)
7. Cause "storm" vs clear weather / transformer failure
8. Premium customers: 41 vs 38

The document also doesn't say if data was lost or what broke the transformer, so the final stage shouldn't claim either.

## Running it
```
pip install anthropic
export ANTHROPIC_API_KEY=...
python pipeline.py --temps 0 0.7 1.0 --runs 5
python evaluate.py runs
python make_report.py runs/temp_0.0/run_1
```
`--mock` just tests the code without calling a model.

## About the included runs
`runs/temp_default/run_1` to `run_5` were all produced by Claude working through the three stages inside a chat session, not through the API. Each is a single run at default sampling (no temperature control), so **there is no temperature sweep in this repo yet**. Stage 2 saw only the facts JSON and stage 3 only facts plus contradictions. The JSON was written by hand into the pipeline's file layout. See each run's `PROVENANCE.txt`. `python pipeline.py` writes the real sweep into `runs/temp_0.0/` etc.

Scores for the 5 in-session runs are in `results/summary_runs.md`. `FAILURE_ANALYSIS.md` contains the generated log plus a manual review. It reports only what actually happened and does not reach 3 failures.

## One-command finish
`./run_all.sh` runs the temperature sweep, scores it, writes `REPORT.md`, and writes `FAILURE_ANALYSIS.md` from the real results.
