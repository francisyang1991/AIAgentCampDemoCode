#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 run_l5_demo.py --setup-only

echo
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  python3 run_l5_demo.py"
echo
echo "Optional demos:"
echo "  APIFY_API_TOKEN=apify_api_... python3 run_l5_demo.py --demo 06"
echo "  OPENAI_API_KEY=sk-... python3 run_l5_demo.py --demo 07 --agent"
