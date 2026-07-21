#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  for candidate in python3.12 python3.11 python3.10 python3.13 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if (3, 10) <= sys.version_info < (3, 14) else 1)
PY
    then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "Could not find Python 3.10–3.13. Please install a supported Python version first."
  exit 1
fi

"$PYTHON_BIN" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ ! -f VOYAGE_API_KEY.txt ]]; then
  cp VOYAGE_API_KEY.example.txt VOYAGE_API_KEY.txt
fi

echo
echo "Setup complete."
echo "1. Paste your Voyage API Key into VOYAGE_API_KEY.txt, or export VOYAGE_API_KEY."
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python 02_chroma_quickstart.py"
echo
echo "ChromaDB will create ./chroma_db automatically on first run."
