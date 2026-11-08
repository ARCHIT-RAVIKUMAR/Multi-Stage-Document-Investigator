#!/bin/sh
# Usage: ./run_all.sh [extra pipeline.py args, e.g. --provider openai --base-url ... --model ...]
set -e
python3 pipeline.py --temps 0 0.7 1.0 --runs 3 "$@"
python3 evaluate.py runs
python3 make_report.py runs/temp_0.0/run_1
python3 make_failure_log.py runs
echo "Done. Check FAILURE_ANALYSIS.md, then commit and send the repo."
