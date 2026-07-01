from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    offline = "--offline" in sys.argv
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    fetch_command = [sys.executable, "fetch_weather.py"]
    if offline:
        fetch_command.append("--offline")
    run(fetch_command)
    run(["node", "tools/generate_dashboard.js"])
    run([sys.executable, "tools/verify_outputs.py"])
    print("\nLocal pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
