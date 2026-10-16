#!/usr/bin/env bash
# Run every agent's tests (needs: pip install -e sdk pytest).
set -e
cd "$(dirname "$0")/.."
for d in agents/*/; do
  [ -d "$d/tests" ] && (cd "$d" && python -m pytest -q)
done
python -m pytest -q sdk
