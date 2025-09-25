#!/bin/bash

set -euo pipefail
if [ -z "$(git status --porcelain)" ]; then
  echo "Function generation did not produce any unexpected changes"
  exit 0
fi

echo "Function generation produced the following unexpected changes:"

git diff | cat

exit 1
