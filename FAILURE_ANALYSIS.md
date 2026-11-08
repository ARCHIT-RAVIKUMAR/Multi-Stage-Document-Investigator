# Failure Analysis Log

Generated from the actual run data by `make_failure_log.py`.

## Temperature summary
| temp | runs | mean recall | fabricated quotes | overreach/pick-side/dropped | false-positive candidates |
|---|---|---|---|---|---|
| temp_0.0 | 3 | 0.67 | 0 | 8 | 0 |
| temp_0.7 | 3 | 0.33 | 2 | 9 | 1 |
| temp_1.0 | 2 | 0.50 | 0 | 7 | 0 |


Total flagged issues across all runs: 62

## Failure 1: bad extraction
- **Run:** `runs/temp_0.7\run_2`
- **Detected issue:** `MISSED_CONTRADICTION C6`
- **Where it started:** Stage 1 never extracted a fact containing ['3 hours'], so stage 2 could not have seen the conflict.
- **Evidence:** `runs/temp_0.7\run_2/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

## Failure 2: bad extraction (hallucinated fact)
- **Run:** `runs/temp_0.7\run_1`
- **Detected issue:** `FABRICATED_QUOTE F16: '02:52 - Failover was approved by Daniel Okafor, Operations Lead.'`
- **Where it started:** Stage 1 produced a quote that is not in the source document; later stages inherit it.
- **Evidence:** `runs/temp_0.7\run_1/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

## Failure 3: final-stage overreach
- **Run:** `runs/temp_0.0\run_1`
- **Detected issue:** `PICKED_SIDE C1: only '02:14' stated as established`
- **Where it started:** Stage 3 stated as established something the document leaves open or contradicts.
- **Evidence:** `runs/temp_0.0\run_1/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

## Failure 4: missed contradiction
- **Run:** `runs/temp_0.0\run_1`
- **Detected issue:** `MISSED_CONTRADICTION C1`
- **Where it started:** Both sides were extracted as separate facts, but stage 2 did not flag them.
- **Evidence:** `runs/temp_0.0\run_1/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

## Failure 5: missed contradiction
- **Run:** `runs/temp_0.0\run_1`
- **Detected issue:** `MISSED_CONTRADICTION C3`
- **Where it started:** Both sides were extracted as separate facts, but stage 2 did not flag them.
- **Evidence:** `runs/temp_0.0\run_1/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`

## Failure 6: missed contradiction
- **Run:** `runs/temp_0.0\run_1`
- **Detected issue:** `MISSED_CONTRADICTION C7`
- **Where it started:** Both sides were extracted as separate facts, but stage 2 did not flag them.
- **Evidence:** `runs/temp_0.0\run_1/stage1_facts.json`, `stage2_contradictions.json`, `stage3_final.json`
