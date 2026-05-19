#!/usr/bin/env python3
"""Check the Claude Code plugin contract for the KR PIPA/DPA workflow.

This is a local static smoke. It does not install Claude Code plugins or call a
live LLM. It verifies that the marketplace exposes `privacy-legal`, that the
plugin contains `/privacy-legal:kr-pipa-dpa-review`, and that the synthetic
sample and expected review fixtures exist.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / "privacy-legal" / ".claude-plugin" / "plugin.json"
SKILL = ROOT / "privacy-legal" / "skills" / "kr-pipa-dpa-review" / "SKILL.md"
SAMPLE = ROOT / "tests" / "fixtures" / "kr_pipa_dpa_review" / "sample_vendor_dpa.md"
EXPECTED = ROOT / "tests" / "fixtures" / "kr_pipa_dpa_review" / "expected_review_skeleton.md"


def main() -> int:
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))

    plugin_entries = marketplace.get("plugins", [])
    privacy_entry = next((p for p in plugin_entries if p.get("name") == "privacy-legal"), None)
    if not privacy_entry:
        raise SystemExit("marketplace.json does not expose privacy-legal")
    if privacy_entry.get("source") != "./privacy-legal":
        raise SystemExit("privacy-legal marketplace source must be ./privacy-legal")
    if plugin.get("name") != "privacy-legal":
        raise SystemExit("privacy-legal plugin.json name mismatch")

    skill_text = SKILL.read_text(encoding="utf-8")
    required_skill_markers = [
        "name: kr-pipa-dpa-review",
        "tests/fixtures/kr_pipa_dpa_review/sample_vendor_dpa.md",
        "tests/fixtures/kr_pipa_dpa_review/expected_review_skeleton.md",
        "requires_professional_review",
    ]
    for marker in required_skill_markers:
        if marker not in skill_text:
            raise SystemExit(f"skill missing marker: {marker}")

    for path in [SAMPLE, EXPECTED]:
        if not path.is_file():
            raise SystemExit(f"missing fixture: {path.relative_to(ROOT)}")

    print("Claude plugin contract ok: privacy-legal exposes kr-pipa-dpa-review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

