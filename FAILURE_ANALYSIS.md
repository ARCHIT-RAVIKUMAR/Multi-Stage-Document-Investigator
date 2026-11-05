# Failure Analysis Log

Generated from the actual run data by `make_failure_log.py`.

## Temperature summary
| temp | runs | mean recall | fabricated quotes | overreach/pick-side/dropped | false-positive candidates |
|---|---|---|---|---|---|
| temp_default | 5 | 1.00 | 0 | 1 | 2 |


Total flagged issues across all runs: 1

**Only 1 distinct failure(s) were found in these runs**, fewer than the 3 the task asks for. Run more times (`--runs 10`) or at higher temperatures rather than padding this log.

## Failure 1: final-stage overreach
- **Run:** `runs/temp_default/run_2`
- **Detected issue:** `PICKED_SIDE C5: only '15 minutes' stated as established`
- **Where it started:** Stage 3 stated as established something the document leaves open or contradicts.
- **Evidence:** `runs/temp_default/run_2/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

---

## Manual review of flagged items (added by hand, not generated)

These are the only things the heuristics flagged across the 5 runs. None is a confirmed hard failure, and no failures were invented to reach the target of 3.

1. **`run_2` PICKED_SIDE C5 (heuristic flag, borderline).** Stage 3 listed "The UPS system is rated for 15 minutes at full load" as established. That is a rating, not a claim about how long the UPS actually ran, and the UPS-runtime conflict (15 vs 9 minutes) is still listed as unresolved. The evaluator matched the "15 minutes" string, so this is mostly a false alarm. The wording is still a weak spot: a reader could mistake the rating for the observed runtime.
2. **`run_2` X9 (false-positive candidate).** Stage 2 flagged "11 hours of fuel" vs "Generator B shut down at 04:10" at low confidence. It only holds if the shutdown was fuel-related, which the facts never say. Stage 3 kept it in the unresolved list, as the rules require.
3. **`run_4` X6 (false-positive candidate).** Stage 2 flagged "UPS rated 15 minutes" vs "ran 9 minutes" at low confidence. It assumes full load, which is not stated. It was labeled low confidence with the assumption spelled out, as the prompt asks.

**Honest conclusion:** across 5 in-session runs, recall was 8/8 every time, there were 0 fabricated quotes, 0 phantom citations and 0 dropped conflicts. The only weaknesses seen were two low-confidence over-flags and one ambiguous established finding. A real failure count needs the API sweep (`./run_all.sh`), where higher temperatures are more likely to surface fabricated quotes or overreach.
