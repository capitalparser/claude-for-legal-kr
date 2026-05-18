# Korean Law MCP Setup For Claude For Legal KR

## Purpose

`claude-for-legal-kr` should use `chrisryugj/korean-law-mcp` as the first
Korean legal source connector. The connector wraps Law.go.kr Open API data and
provides citation verification, source retrieval, time comparison, and Korean
law search workflows.

This repository does not vendor `korean-law-mcp`. Keep it as an external MCP
dependency unless an ADR approves a different approach.

## Setup Options

### Claude Code Plugin

The upstream `korean-law-mcp` README documents Claude Code plugin installation:

```text
/plugin marketplace add chrisryugj/korean-law-mcp
/plugin install korean-law@korean-law-marketplace
```

During install, provide the Law.go.kr Open API key (OC). The key must not be
committed to this repository.

## User API Hook

When a test needs live Law.go.kr access, the user should attach the API key only
as a local environment variable:

```bash
export LAW_OC="<your-law-go-kr-oc-key>"
python3 scripts/korean_law_mcp_smoke.py
```

Alternative variable:

```bash
export KOREAN_LAW_API_KEY="<your-law-go-kr-oc-key>"
python3 scripts/korean_law_mcp_smoke.py
```

Do not write either value into `.env`, git-tracked docs, fixtures, screenshots,
logs, or test output.

The smoke script calls the CLI binary through:

```bash
npx -y -p korean-law-mcp@latest korean-law search_law --query "개인정보 보호법" --display 5
```

Do not call `npx korean-law-mcp@latest search_law ...` for this smoke test. That
invokes the MCP stdio server binary, which waits for MCP protocol messages and
can look like a timeout.

### Local MCP Install

For local client setup, the upstream project documents:

```bash
npx korean-law-mcp setup
```

This runs the connector setup wizard and registers the MCP server with a
supported client.

## Expected Tool Behavior

Korea-facing skills should use the connector to:

- retrieve current statute text,
- verify article citations,
- search Korean case law and administrative materials,
- detect missing or fabricated citations,
- distinguish `verified_source` from `model_inference`.

If the MCP returns `[NOT_FOUND]`, `[HALLUCINATION_DETECTED]`, an empty result,
or any tool error, the skill must not silently complete the legal conclusion.
It should report the failed lookup and mark the issue as unverified.

## Initial PIPA/DPA Queries

For `/privacy-legal:kr-pipa-dpa-review`, start with queries like:

```text
개인정보 보호법 제26조 처리위탁
개인정보 보호법 제28조의8 개인정보 국외 이전
개인정보 보호법 제29조 안전성 확보조치
개인정보 보호법 제34조 유출 통지 신고
개인정보 처리위탁 제3자 제공 판례
```

## Source Labels

Skills should preserve these labels in outputs:

- `verified_source`: retrieved or verified through MCP in the current workflow.
- `user_supplied_unverified`: user-supplied text not independently retrieved.
- `model_inference`: model-derived statement without retrieval evidence.
- `requires_professional_review`: final external use is blocked until review.

## Open Integration Work

- Confirm exact `korean-law-mcp` tool names exposed in the local Claude Code
  plugin runtime.
- Run `python3 scripts/korean_law_mcp_smoke.py` once a Law.go.kr Open API key is
  configured.
- Add fixtures for representative MCP responses so CI does not require live
  legal-source access.
