#!/bin/bash
set -euo pipefail
DIFF="$(git status src/harness setup.py -s)"
if [[ $DIFF ]]; then
    echo "Working directory is not clean:"
    echo $DIFF | sed 's/^/  /'
    false
else
    true
fi
