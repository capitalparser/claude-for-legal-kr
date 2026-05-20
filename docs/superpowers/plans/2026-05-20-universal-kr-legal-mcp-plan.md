# Universal KR Legal MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reposition the fork as a provider-neutral Korean legal workflow MCP for non-lawyer business users, while keeping specialist review gates.

**Architecture:** Add a thin stdio MCP-compatible server that exposes generic Korean legal workflow tools. The server does not call an LLM provider; it returns Korean legal source results and structured workflow payloads that any MCP-capable LLM client can use.

**Tech Stack:** Python standard library, JSON-RPC over stdio, existing markdown skill/playbook files, existing `korean-law-mcp` source connector through `npx` when live source lookup is enabled.

---

### Task 1: Product Positioning

**Files:**
- Modify: `README.md`
- Modify: `docs/implementation/generic-llm-adapter-contract.md`

- [ ] **Step 1: Move README framing away from DPA-specific positioning**

Update the first section to say the project is a Korean legal workflow MCP for legal non-specialists and company operators. Keep the upstream Apache-2.0 attribution and the attorney/professional review gate.

- [ ] **Step 2: Keep PIPA/DPA as an example, not the product center**

Describe PIPA/DPA as the first preset/example under a wider `kr_legal_review` workflow.

- [ ] **Step 3: Update generic adapter docs**

State that the universal surface is MCP-first and provider-neutral. Claude Code is one client, not the product boundary.

### Task 2: MCP Server Scaffold

**Files:**
- Create: `scripts/kr_legal_workflow_mcp.py`
- Modify: `tests/test_kr_pipa_dpa_skill.py`

- [ ] **Step 1: Add static tests for generic tool names**

Add assertions that the MCP server exposes `kr_legal_source_search` and `kr_legal_review`, and that docs mention provider-neutral MCP use.

- [ ] **Step 2: Implement stdio JSON-RPC handlers**

Support `initialize`, `tools/list`, and `tools/call`. Unknown methods return JSON-RPC error `-32601`.

- [ ] **Step 3: Implement `kr_legal_source_search`**

Accept `query`, `law_name`, `article_numbers`, and `live_lookup`. With `live_lookup=false`, return planned source lookup steps. With `live_lookup=true`, call `npx -y korean-law-mcp@latest` using the local `LAW_OC`/`KOREAN_LAW_API_KEY` environment.

- [ ] **Step 4: Implement `kr_legal_review`**

Accept `question`, `document_text`, `matter_context`, and `preset`. Return a provider-neutral review payload containing source lookup plan, workflow instructions, source status rules, and review gate.

### Task 3: Verification And Commit

**Files:**
- Modify: tests and docs from Tasks 1-2

- [ ] **Step 1: Run focused tests**

Run `uv run pytest tests/test_kr_pipa_dpa_skill.py`.

- [ ] **Step 2: Run script sanity checks**

Run `python3 -m py_compile scripts/kr_legal_workflow_mcp.py` and a local JSON-RPC `tools/list` smoke.

- [ ] **Step 3: Run vault verification**

Run `./Harness/verify.sh` from `/Users/kjun/vault`.

- [ ] **Step 4: Commit only scoped files**

Do not include the pre-existing `CONTEXT.md` local modification unless the user explicitly asks for it.
