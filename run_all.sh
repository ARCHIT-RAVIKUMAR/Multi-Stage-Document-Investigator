#!/bin/sh
# One command to produce everything: python deps must be installed and ANTHROPIC_API_KEY set.
set -e
python3 pipeline.py --temps 0 0.7 1.0 --runs 3
python3 evaluate.py runs
python3 make_report.py runs/temp_0.0/run_1
python3 make_failure_log.py runs
echo "Done. Review FAILURE_ANALYSIS.md, then upload the folder."
