#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  for candidate in python3.12 python3.11 python3.10 python3.13 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
    then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "Could not find Python 3.10+. Please install Python 3.10+ first."
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys

if sys.version_info < (3, 10):
    print("Python 3.10+ is required. Current version:", sys.version.split()[0])
    raise SystemExit(1)
print("Using Python", sys.version.split()[0])
PY

"$PYTHON_BIN" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "Setup complete."
echo
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  python 01_hello_agent.py"
echo
echo "Model setup:"
echo "  OpenAI: export OPENAI_API_KEY=\"sk-...\""
echo "  Ollama: install Ollama, then run: ollama pull qwen2.5:7b"
echo "  Other OpenAI-compatible model: set OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_MODE=chat_completions"
echo
if command -v cursor >/dev/null 2>&1; then
  echo "Cursor tip: run 'cursor .' to open this folder in Cursor."
fi
