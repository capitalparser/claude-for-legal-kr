#!/usr/bin/env python3
"""Live smoke test for korean-law-mcp.

This script is intentionally API-key gated:

- Without LAW_OC or KOREAN_LAW_API_KEY, it exits 0 with a skip message.
- With a key, it runs the npm-published korean-law-mcp CLI via npx and verifies
  that a basic PIPA law search returns the expected law name and identifier.

Do not print the API key or commit local key files.
"""
from __future__ import annotations

import os
import subprocess
import sys


QUERY = "개인정보 보호법"


def main() -> int:
    law_oc = os.environ.get("LAW_OC") or os.environ.get("KOREAN_LAW_API_KEY")
    if not law_oc:
        print("skip: LAW_OC or KOREAN_LAW_API_KEY is not set")
        print("set one locally, then run: python3 scripts/korean_law_mcp_smoke.py")
        return 0

    env = os.environ.copy()
    env["LAW_OC"] = law_oc

    command = [
        "npx",
        "-y",
        "korean-law-mcp@latest",
        "search_law",
        "--query",
        QUERY,
        "--display",
        "5",
    ]

    result = subprocess.run(
        command,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        text=True,
        capture_output=True,
        timeout=45,
        check=False,
    )

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        print("korean-law-mcp smoke failed", file=sys.stderr)
        print(_redact(combined), file=sys.stderr)
        return result.returncode

    if QUERY not in combined or ("MST" not in combined and "법령ID" not in combined):
        print("korean-law-mcp smoke returned unexpected output", file=sys.stderr)
        print(_redact(combined), file=sys.stderr)
        return 1

    print("korean-law-mcp smoke ok: PIPA search returned law identifiers")
    return 0


def _redact(text: str) -> str:
    for key_name in ("LAW_OC", "KOREAN_LAW_API_KEY"):
        key = os.environ.get(key_name)
        if key:
            text = text.replace(key, "***")
    return text


if __name__ == "__main__":
    raise SystemExit(main())

