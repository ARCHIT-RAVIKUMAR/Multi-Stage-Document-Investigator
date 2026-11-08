# Analysis of live runs

Model: `openai/gpt-oss-20b` on Groq. Temperatures 0.0, 0.7, 1.0. Runs completed: 3, 3 and 2 (the third run at 1.0 hit Groq's daily token limit and was removed, not scored). Every run's stage JSON is in `runs/`; the first attempt, which failed on JSON formatting, is in `runs_attempt1/`.

## Temperature comparison

| temp | runs | mean recall (of 8 planted) | non-verbatim quotes | overreach / pick-side / dropped |
|---|---|---|---|---|
| 0.0 | 3 | 0.67 | 0 | 8 |
| 0.7 | 3 | 0.33 | 2 | 9 |
| 1.0 | 2 | 0.50 | 0 | 7 |

With 2-3 runs per setting this is too small to claim a temperature effect. Recall was not monotonic, and temperature 0.0 was not clean. What does stand out is that the start-time (C1) and customer-count (C3) contradictions were missed in 7 of 8 runs, including all three at 0.0, which points to a prompt or stage weakness, not sampling noise. The only temperature-linked difference I can point to is the two quote problems at 0.7 (see below). Minor: four runs (all three at 0.0, one at 0.7) contained empty-string entries in the facts list; the scorer ignores those and logs them as `MALFORMED_ITEMS`.

## Three incorrect conclusions (run `temp_0.0/run_1`)

### Failure 1: final stage turns an attribution into an established cause
- **Stage 3 said:** "The outage was caused by a transformer failure at Substation 7, as reported by the utility provider." The final conclusion repeats it: the outage happened "due to a transformer failure at Substation 7."
- **Document says:** only that the utility provider *attributed* the loss to a transformer failure (Section 7). Section 1 says a storm triggered it, Section 7 says the skies were clear, and Section 1 also says the root cause is still under investigation.
- **Cause:** final-stage overreach. Stage 3 took fact F32 (an attribution) as settled and ignored F7 (storm), which stage 2 never flagged against it. It also contradicts its own fourth finding ("root cause remains under investigation"), so the report disagrees with itself.
- **Category:** overreach in the final stage, helped by a missed contradiction in stage 2.

### Failure 2: stage 3 asserts "4 hours 20 minutes" even though restoration time was flagged as conflicting
- **Stage 3 said:** the outage "lasted 4 hours 20 minutes", and the conclusion calls it a "4-hour 20-minute outage."
- **Evidence:** stage 2 flagged F3 (restored 06:34) vs F18 (restored 08:05). The 4h20m figure (F4) is only valid if 06:34 is right.
- **Cause:** stage 2 listed only `F3` and `F18` in that contradiction, not `F4`. Stage 3's rule is to avoid facts that appear in a flagged contradiction, and it applied the rule by fact ID only, so it did not notice that F4 depends on F3. The same finding states "312 customers", which has its own unreported conflict (Failure 3).
- **Category:** the rule "don't rely on conflicted facts" does not cover facts that depend on them. A prompt design weakness, not just a model slip.

### Failure 3: stage 2 missed contradictions even though stage 1 extracted both sides
- **Missed:** 312 customers (F5) vs 213 customers (F24); 41 premium (F24) vs 38 premium (F35); storm (F7) vs clear skies and transformer failure (F31, F32). Stage 2 flagged only 4 conflicts out of the 8 planted.
- **Check:** all of these facts are present in stage 1 (38 facts), so the extraction was not at fault.
- **Cause:** missed contradiction in stage 2. With 38 facts and no grouping by topic, it caught conflicts where the wording was close (UPS 15 vs 9 minutes, 06:34 vs 08:05) but not where it differed ("affected" vs "experienced degraded or no service"). F24 also packs two numbers (213 and 41) into one fact, making the comparison harder.
- **Category:** missed contradiction. Failures 1 and 2 follow from it, since stage 3 never heard about these conflicts.

## Do the failures repeat? (the three temperature 0.0 runs)

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| Valid contradictions flagged by stage 2 | 4 | 6 | 6 |
| 02:14 vs 02:41 (start time) flagged | no | no | no |
| 312 vs 213 (customers) flagged | no | no | no |
| Stage 3 states 02:14, 4h20m and 312 as established | yes | yes | yes |
| Stage 3 states 4h20m although the 06:34 vs 08:05 conflict was flagged | yes | yes | yes |
| Transformer failure stated as the cause | yes | no (worded as "the provider attributed...") | no |
| Established finding uses a fact from a flagged conflict | via F4 | via F4 | F31 (weather) and F4 |

Takeaways:
- **Temperature 0.0 gave consistent errors, not correct answers.** All three runs asserted the same three headline numbers (02:14 start, 4h20m duration, 312 customers) as fact, although the document contradicts each of them.
- **Temperature 0.0 was not fully deterministic.** Stage 2 flagged 4 conflicts in run 1 but 6 in runs 2 and 3, from nearly identical stage 1 output. Groq converts temperature 0 to a tiny positive value, so exact repeatability should not be assumed.
- **Failure 1 (transformer stated as the cause) did not repeat**: run 2 worded it correctly as an attribution. It happened in 1 of 3 runs, which I would report as is.
- **Failure 2 (4h20m asserted despite a flagged restoration conflict) repeated in all three runs**, which supports the explanation that the final stage only checks fact IDs, not facts that depend on them.

### Additional failure (run 3): the final report contradicts itself
- **Stage 3 listed as established:** "The regional weather station recorded clear skies, no precipitation..." (fact F31).
- **But F31 is half of a conflict stage 2 flagged** (C4: storm vs clear skies), and the conclusion names "weather conditions" as unresolved.
- **Cause:** direct violation of the stage 3 rule "do not use a fact that is part of an unresolved contradiction". The model followed the rule for some facts and not others.
- **Category:** final-stage rule violation.

### Smaller observations
- Run 2's "established findings" included trivia unrelated to the incident (when Building 2 opened, the sunrise time, a service date). Stage 1 had extracted these despite being told to ignore irrelevant details, and stage 3 repeated them.
- In runs 2 and 3, stage 1 dropped the source from the fuel fact ("The fuel vendor's refuel log shows..." became "Generator B's tank at 20 percent..."). The conflict still got flagged, but a later stage cannot see who said what.
- Run 3's explanation of the restoration conflict ("implying service was restored before the feed") is muddled, though the conflict itself is real.

## Caveats and secondary observations
- C1 (02:14 vs 02:41) is arguably ambiguous in my answer key: the power could be lost at 02:14 and the alarm raised at 02:41. Missing it is only partly the model's fault.
- Stage 1 extracted irrelevant facts (the parking lot repaving, the sunrise time) even though the prompt says to skip them. Minor.
- At 0.7, two quotes were not verbatim: one splices two lines of the timeline, and one drops the word "full" from a real sentence. The facts were real; the quotes broke the verbatim rule. These are not hallucinated facts.

## Likely fixes (not yet tested)
1. Stage 2: group facts by topic (times, counts, people, causes) and compare within groups.
2. Stage 1: split bundled facts into one number per fact.
3. Stage 3: add "any fact derived from a conflicted fact is also unresolved", and "an attribution is not an established cause."
