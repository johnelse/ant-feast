#!/bin/bash
# Draw a level's picture, generate a hard deal for it, and check it, in one go.
#
#   tools/pipeline.sh "Level name" tools/art/script.py LEVEL_INDEX [DEBUG_PORT=9301]
#
# 1. installs the picture (40x40) from the drawing script, dropping the old deal
# 2. generates a deal (300 candidates); while the score is above 0.06, keeps
#    climbing from the best deal with up to two more 600-candidate runs
#    (seeds 2 and 3), installing each improvement
# 3. replays the stored solution with test/sim.html?only=NAME
#
# Needs tools/serve.py running on port 8766. Generator output goes to
# tools/out/p_INDEX, p2_INDEX and p3_INDEX. LEVEL_INDEX is the level's
# position in LEVELS, counting from 0. A run takes about 5-25 minutes on a
# 4-core laptop. A score still well above 0.15 at the end usually means the
# picture needs more detail, not more search (see AGENTS.md).
set -e
NAME=$1; SCRIPT=$2; IDX=$3; PORT=${4:-9301}
if [ -z "$IDX" ]; then
  echo "usage: tools/pipeline.sh \"Level name\" tools/art/script.py LEVEL_INDEX [DEBUG_PORT]" >&2
  exit 2
fi
SCRIPT=$(realpath "$SCRIPT")
cd "$(dirname "$0")/.."
GEN="http://127.0.0.1:8766/test/generate.html?level=$IDX&objective=sustained&trials=8&report=40&min=10&max=40"

score() { grep -o 'score=[0-9.]*' "$1" | cut -d= -f2; }
weak() { python3 -c "import sys; sys.exit(0 if $1 > 0.06 else 1)"; }
run() {  # run OUT_NAME EXTRA_PARAMS
  tools/runpage.sh "$GEN&$2&post=/$1" "$PORT" 5400
  grep -v "deal:\|solution:" "tools/out/$1"
  python3 tools/art/install.py deal "$NAME" "tools/out/$1"
}

python3 tools/art/install.py picture "$SCRIPT" 40 "$NAME"
run "p_$IDX" "iterations=300"
if weak "$(score "tools/out/p_$IDX")"; then
  run "p2_$IDX" "iterations=600&continue=1&seed=2"
  if weak "$(score "tools/out/p2_$IDX")"; then
    run "p3_$IDX" "iterations=600&continue=1&seed=3"
  fi
fi
ONLY=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$NAME")
tools/runpage.sh "http://127.0.0.1:8766/test/sim.html?only=$ONLY" "$PORT" 600 | sed 's/&gt;/>/g'
echo PIPELINE DONE
