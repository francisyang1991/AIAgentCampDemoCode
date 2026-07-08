"""
One-command runner for L5 demo_code.

Common use:
    python3 run_l5_demo.py

Optional Apify demo:
    export APIFY_API_TOKEN="apify_api_..."
    python3 run_l5_demo.py --demo 06

Optional Agent mode:
    export OPENAI_API_KEY="sk-..."
    python3 run_l5_demo.py --demo 07 --agent

The individual demo files are still useful for teaching. This runner exists so
students have one reliable entry point when their shell/Python environment is
messy.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
VENV_PYTHON = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

DEMOS = {
    "01": ["01_minimal_mcp_server.py", "--selftest"],
    "02": ["02_connect_stdio.py"],
    "03": ["03_filesystem_server.py"],
    "04": ["04_resources_demo.py"],
    "05": ["05_your_mcp_agent.py"],
    "06": ["06_apify_linkedin_jobs_mcp.py"],
    "07": ["07_agent_autonomous_mcp.py"],
}

DEFAULT_ORDER = ["01", "02", "04", "03", "05", "07"]
COMMON_NODE_DIRS = [
    Path("/opt/homebrew/bin"),
    Path("/usr/local/bin"),
    Path.home() / ".nvm/current/bin",
]
PREFERRED_PYTHONS = ["python3.12", "python3.11", "python3.10", "python3"]
PLACEHOLDERS = {
    "sk-...",
    "sk-your-key-here",
    "apify_api_...",
    "apify_api_your-token-here",
    "your-provider-key",
    "your-model-name",
    "gpt-your-model-name",
    "https://your-provider.example/v1",
}


def _load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or value in PLACEHOLDERS or key in os.environ:
            continue
        os.environ[key] = value


def _env_with_node_path(env: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(os.environ if env is None else env)
    parts = [str(p) for p in COMMON_NODE_DIRS if p.exists()]
    current = merged.get("PATH", "")
    merged["PATH"] = os.pathsep.join([*parts, current]) if parts else current
    return merged


def _which_npx() -> str | None:
    return shutil.which("npx", path=_env_with_node_path().get("PATH"))


def _base_python() -> str:
    for name in PREFERRED_PYTHONS:
        path = shutil.which(name, path=_env_with_node_path().get("PATH"))
        if path:
            return path
    return sys.executable


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
    print("\n" + "=" * 78, flush=True)
    print("$", " ".join(cmd), flush=True)
    print("=" * 78, flush=True)
    completed = subprocess.run(cmd, cwd=ROOT, env=_env_with_node_path(env))
    return completed.returncode


def _create_venv() -> None:
    print(f"Creating virtualenv: {VENV_DIR}")
    subprocess.run([_base_python(), "-m", "venv", str(VENV_DIR)], check=True, cwd=ROOT)


def _deps_ok() -> bool:
    if not VENV_PYTHON.exists():
        return False
    code = "import agents, mcp; print('deps ok')"
    return subprocess.run(
        [str(VENV_PYTHON), "-c", code],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_env() -> None:
    if not VENV_PYTHON.exists():
        _create_venv()

    if not _deps_ok():
        print("Installing Python deps from requirements.txt ...")
        subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            cwd=ROOT,
        )


def check_node() -> None:
    npx = _which_npx()
    if npx:
        print(f"npx: found ({npx})")
    else:
        print("npx: NOT FOUND. Demo 03/05 filesystem server and 06 Apify need Node.js.")


def run_demo(demo_id: str, *, agent_mode: bool = False) -> int:
    if demo_id not in DEMOS:
        print(f"Unknown demo id: {demo_id}. Choose one of: {', '.join(DEMOS)}")
        return 2

    if demo_id == "06" and not os.getenv("APIFY_API_TOKEN"):
        print("\nSkipping 06: APIFY_API_TOKEN is not set.")
        print('Run it with: export APIFY_API_TOKEN="apify_api_..." && python3 run_l5_demo.py --demo 06')
        return 0

    env = os.environ.copy()
    if agent_mode:
        env["RUN_AGENT_DEMO"] = "1"

    return _run([str(VENV_PYTHON), *DEMOS[demo_id]], env=env)


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(description="Run L5 MCP demo_code reliably.")
    parser.add_argument(
        "--demo",
        choices=sorted(DEMOS),
        help="Run one demo only. Default runs 01, 02, 04, 03, 05.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run 01-06. Demo 06 is skipped unless APIFY_API_TOKEN is set.",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Also run optional Agent mode inside demos that support it.",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Create .venv and install deps, then stop.",
    )
    args = parser.parse_args()

    ensure_env()
    check_node()

    if args.setup_only:
        print("\nSetup complete.")
        return 0

    order = [args.demo] if args.demo else (list(DEMOS) if args.all else DEFAULT_ORDER)

    failed: list[str] = []
    for demo_id in order:
        code = run_demo(demo_id, agent_mode=args.agent)
        if code != 0:
            failed.append(demo_id)

    if failed:
        print(f"\nFAILED demos: {', '.join(failed)}")
        return 1

    print("\nAll selected L5 demos finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
