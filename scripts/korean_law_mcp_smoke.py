#!/usr/bin/env python3
"""Live smoke test for korean-law-mcp.

This script is intentionally API-key gated:

- Without LAW_OC or KOREAN_LAW_API_KEY, it exits 0 with a skip message.
- With a key, it runs the npm-published korean-law CLI from the korean-law-mcp
  package via npx and verifies that a basic PIPA law search returns the
  expected law name and identifier.

Do not print the API key or commit local key files.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys


QUERY = "개인정보 보호법"
PIPA_CORE_ARTICLES = ("제26조", "제28조의8", "제29조", "제34조")


def main() -> int:
    law_oc = os.environ.get("LAW_OC") or os.environ.get("KOREAN_LAW_API_KEY")
    if not law_oc:
        print("skip: LAW_OC or KOREAN_LAW_API_KEY is not set")
        print("set one locally, then run: python3 scripts/korean_law_mcp_smoke.py")
        return 0

    env = os.environ.copy()
    env["LAW_OC"] = law_oc

    search_result = _run_korean_law(
        env,
        [
            "search_law",
            "--query",
            QUERY,
            "--display",
            "5",
        ],
    )
    if search_result.returncode != 0:
        return search_result.returncode

    combined = search_result.output
    if QUERY not in combined or ("MST" not in combined and "법령ID" not in combined):
        print("korean-law-mcp smoke returned unexpected output", file=sys.stderr)
        print(_redact(combined), file=sys.stderr)
        return 1

    mst = _extract_mst(combined)
    if not mst:
        print("korean-law-mcp smoke could not parse MST from search output", file=sys.stderr)
        print(_redact(combined), file=sys.stderr)
        return 1

    print("korean-law-mcp smoke ok: PIPA search returned law identifiers")

    for article in PIPA_CORE_ARTICLES:
        article_result = _run_korean_law(
            env,
            [
                "get_law_text",
                "--mst",
                mst,
                "--jo",
                article,
            ],
        )
        if article_result.returncode != 0:
            return article_result.returncode
        if article not in article_result.output and article.replace("의", "-") not in article_result.output:
            print(f"korean-law-mcp smoke returned unexpected output for {article}", file=sys.stderr)
            print(_redact(article_result.output), file=sys.stderr)
            return 1

    print("PIPA deep smoke ok: core articles returned text")
    return 0


class CommandResult:
    def __init__(self, returncode: int, output: str) -> None:
        self.returncode = returncode
        self.output = output


def _run_korean_law(env: dict[str, str], args: list[str]) -> CommandResult:
    command = [
        "npx",
        "-y",
        "-p",
        "korean-law-mcp@latest",
        "korean-law",
        *args,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=env,
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        combined = (exc.stdout or "") + "\n" + (exc.stderr or "")
        print("korean-law-mcp smoke timed out", file=sys.stderr)
        print("command should invoke the korean-law CLI, not the MCP stdio server", file=sys.stderr)
        if combined.strip():
            print(_redact(combined), file=sys.stderr)
        return CommandResult(124, combined)

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        print("korean-law-mcp smoke failed", file=sys.stderr)
        print(_redact(combined), file=sys.stderr)
        return CommandResult(result.returncode, combined)

    return CommandResult(0, combined)


def _extract_mst(text: str) -> str | None:
    match = re.search(r"MST:\s*(\d+)", text)
    if match:
        return match.group(1)
    return None


def _redact(text: str) -> str:
    for key_name in ("LAW_OC", "KOREAN_LAW_API_KEY"):
        key = os.environ.get(key_name)
        if key:
            text = text.replace(key, "***")
    return text


if __name__ == "__main__":
    raise SystemExit(main())
