#!/usr/bin/env bash
# Run every agent's tests, the template's and the SDK's (needs: pip install -e sdk pytest).
set -e
cd "$(dirname "$0")/.."
for d in agents/*/ template/; do
  [ -d "$d/tests" ] && (cd "$d" && python -m pytest -q -p no:cacheprovider)
done
python -m pytest -q sdk
