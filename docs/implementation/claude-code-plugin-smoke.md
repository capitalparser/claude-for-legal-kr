# Claude Code Plugin Smoke

## Purpose

This smoke verifies that the Claude Code plugin path is usable before claiming
the workflow is ready for actual LLM use.

It covers two levels:

1. Static contract: `marketplace.json` exposes `privacy-legal`, and the plugin
   contains `kr-pipa-dpa-review`.
2. Manual LLM run: Claude Code can run the command on the synthetic DPA fixture
   and produce a review matching `expected_review_skeleton.md`.

## Static Contract Smoke

Run:

```bash
cd /Users/kjun/vault/01_Projects/claude-for-legal-kr
python3 scripts/check_claude_plugin_contract.py
```

Expected:

```text
Claude plugin contract ok: privacy-legal exposes kr-pipa-dpa-review
```

This checks:

- `.claude-plugin/marketplace.json`
- `privacy-legal/.claude-plugin/plugin.json`
- `privacy-legal/skills/kr-pipa-dpa-review/SKILL.md`
- `tests/fixtures/kr_pipa_dpa_review/sample_vendor_dpa.md`
- `tests/fixtures/kr_pipa_dpa_review/expected_review_skeleton.md`

## Claude Code Install Smoke

Inside Claude Code:

```text
/plugin marketplace add /Users/kjun/vault/01_Projects/claude-for-legal-kr
/plugin install privacy-legal@claude-for-legal
```

Restart Claude Code, then confirm the command is available:

```text
/privacy-legal:kr-pipa-dpa-review
```

## End-To-End Sample DPA Smoke

Run:

```text
/privacy-legal:kr-pipa-dpa-review tests/fixtures/kr_pipa_dpa_review/sample_vendor_dpa.md
```

Compare against:

```text
tests/fixtures/kr_pipa_dpa_review/expected_review_skeleton.md
```

Required output features:

- `Verdict: conditional`
- `required gaps`
- `recommended improvements`
- `source status`
- `requires_professional_review`
- AI training issue
- subprocessor / 재위탁 issue
- breach notification issue
- PIPA anchors: 제26조, 제28조의8, 제29조, 제34조

## Live Source Precondition

Before relying on `verified_source`, run:

```bash
export LAW_OC="<법제처 Open API OC 키>"
python3 scripts/korean_law_mcp_smoke.py
```

Expected:

```text
PIPA deep smoke ok: core articles returned text
```

Do not commit API keys, `.env` files, screenshots, or logs containing keys.

