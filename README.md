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
- `runs/temp_0.0`, `runs/temp_0.7`, `runs/temp_1.0` are live runs on Groq (`openai/gpt-oss-20b`): 3, 3 and 2 runs. The third run at 1.0 hit the free-tier daily token limit and was removed. Every stage's JSON is saved there.
- `runs_attempt1/` is an earlier live attempt that failed on invalid JSON and empty replies, kept as evidence.
- `runs/temp_default/run_1` to `run_5` were written by Claude inside a chat session, not through the API (see each `PROVENANCE.txt`). They are not part of the temperature comparison.
- `REPORT.md` is the final report generated from `runs/temp_0.0/run_1`.
- `ANALYSIS.md` has the temperature comparison and three incorrect conclusions with causes. `FAILURE_ANALYSIS.md` is the auto-generated triage list.

## One-command finish
`./run_all.sh` runs the temperature sweep, scores it, writes `REPORT.md`, and writes `FAILURE_ANALYSIS.md` from the real results.

## Running with a live model
Anthropic: `export ANTHROPIC_API_KEY=...` then `./run_all.sh`

Groq (free tier):
```
pip install openai && export LLM_API_KEY=your_groq_key
./run_all.sh --provider openai --base-url https://api.groq.com/openai/v1 --model openai/gpt-oss-20b
```
Gemini (free tier):
```
pip install openai && export LLM_API_KEY=your_gemini_key
./run_all.sh --provider openai --base-url https://generativelanguage.googleapis.com/v1beta/openai/ --model gemini-2.0-flash
```
This writes `runs/temp_0.0/`, `temp_0.7/`, `temp_1.0/` (3 runs each), re-scores everything, and regenerates `FAILURE_ANALYSIS.md`.
