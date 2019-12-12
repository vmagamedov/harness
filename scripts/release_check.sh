#!/bin/bash
DIFF="$(git status harness setup.py -s)"
if [[ $DIFF ]]; then
    echo "Working directory is not clean:"
    echo $DIFF | sed 's/^/  /'
    false
else
    true
fi
