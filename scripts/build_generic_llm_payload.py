#!/usr/bin/env python3
"""Build a generic LLM payload for KR PIPA/DPA review.

This script does not call an LLM endpoint. It prepares the prompt inputs and
schema references that an OpenAI, Agents SDK, LangChain, or custom adapter would
send to its model runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "privacy-legal" / "skills" / "kr-pipa-dpa-review" / "SKILL.md"
PLAYBOOK = ROOT / "privacy-legal" / "references" / "korea-pipa-dpa-playbook.md"
DEFAULT_DOCUMENT = ROOT / "tests" / "fixtures" / "kr_pipa_dpa_review" / "sample_vendor_dpa.md"
SCHEMA = ROOT / "schemas" / "kr_pipa_dpa_review.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--document",
        default=str(DEFAULT_DOCUMENT),
        help="Path to DPA/contract text. Defaults to sample_vendor_dpa.md.",
    )
    parser.add_argument(
        "--matter-context",
        default="",
        help="Optional matter context to include in the payload.",
    )
    args = parser.parse_args()

    document_path = Path(args.document)
    payload = {
        "system_materials": {
            "skill_name": "kr-pipa-dpa-review",
            "skill_prompt": SKILL.read_text(encoding="utf-8"),
            "playbook_name": "korea-pipa-dpa-playbook",
            "playbook": PLAYBOOK.read_text(encoding="utf-8"),
        },
        "user_materials": {
            "document_path": str(document_path),
            "document_text": document_path.read_text(encoding="utf-8"),
            "matter_context": args.matter_context,
            "source_results": [],
        },
        "response_schema": json.loads(SCHEMA.read_text(encoding="utf-8")),
        "adapter_note": (
            "Before calling the LLM in production, populate source_results with "
            "korean-law-mcp lookups for PIPA Articles 26, 28-8, 29, and 34."
        ),
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
