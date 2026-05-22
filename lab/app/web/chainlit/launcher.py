"""Launch Chainlit with the Chainlit app directory as the project root."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent


def main() -> int:
    """Run Chainlit with APP_DIR pinned as CHAINLIT_APP_ROOT."""
    env = os.environ.copy()
    env["CHAINLIT_APP_ROOT"] = str(APP_DIR)

    command = [
        sys.executable,
        "-m",
        "chainlit",
        "run",
        "app.py",
        *sys.argv[1:],
    ]
    return subprocess.call(command, cwd=str(APP_DIR), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
