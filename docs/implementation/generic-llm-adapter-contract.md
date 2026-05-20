# Generic LLM Adapter Contract

## Purpose

This document defines what is needed to use `claude-for-legal-kr` outside
Claude Code, for example in OpenAI, ChatGPT Apps, LangChain, Cursor, Windsurf,
local models, a custom agent runtime, or another MCP-capable LLM client.

Current status:

- Claude Code plugin runtime: smoke passed.
- Korean law source retrieval: live `korean-law-mcp` smoke passed with a user
  supplied Law.go.kr OC key.
- Generic MCP server: `scripts/kr_legal_workflow_mcp.py` exposes provider-neutral
  `kr_legal_source_search` and `kr_legal_review` tools.
- Generic/OpenAI adapter: LLM provider calls are intentionally not embedded in
  the server. The MCP client/model runtime remains responsible for final
  drafting.

The core idea:

1. Use `korean-law-mcp` as the source retrieval tool.
2. Use `claude-for-legal-kr` as the workflow layer that turns sources into
   issue spotting, gap classification, and review gates.
3. Let the client LLM draft the final answer using the returned source/workflow
   context.

The target user is not necessarily a lawyer. The primary workflow is for a
legal non-specialist, company operator, or individual who needs to understand
what to check before asking counsel or making a business decision. Attorney or
responsible-professional review remains mandatory before external reliance.

## Universal MCP Surface

Run:

```bash
python3 scripts/kr_legal_workflow_mcp.py
```

MCP tools:

- `kr_legal_source_search`
  - Plans or runs Korean legal source lookup.
  - With `live_lookup=false`, returns the lookup plan and source status rules.
  - With `live_lookup=true`, calls `korean-law-mcp` through `npx` when `LAW_OC`
    or `KOREAN_LAW_API_KEY` is set.
- `kr_legal_review`
  - Builds a provider-neutral Korean legal review payload from a question,
    document, or business situation.
  - Supports presets such as `general`, `privacy`, `commercial_contract`,
    `employment`, `corporate`, `tax`, `regulatory`, and `litigation`.
  - Does not claim to produce legal advice or a final legal conclusion.

Claude Code plugins are one runtime surface. The MCP server is the neutral
surface for other LLM clients.

## Required Inputs For Review

- `document_text`: the DPA, contract excerpt, or vendor data-processing terms.
- `matter_context`: optional facts such as controller/processor roles, data
  categories, Korean data subjects, overseas processing, and AI usage.
- `source_results`: results returned by `korean-law-mcp` or another Korean legal
  source connector.
- `question`: optional plain-language legal or compliance question.
- `preset`: optional workflow preset. Defaults to `general`.

## Source Lookup Sequence

For privacy/PIPA reviews, the adapter should run this tool sequence before the
final review:

1. `search_law` for `개인정보 보호법`.
2. Parse `MST` or law identifier.
3. `get_law_text` for:
   - 제26조
   - 제28조의8
   - 제29조
   - 제34조
4. Optional: search case law for 처리위탁 vs 제3자 제공.
5. Optional: retrieve PIPC guidance or official standard entrustment agreement.

If any required source lookup fails, the adapter must not pretend it succeeded.
The relevant statement must be marked `model_inference` or
`user_supplied_unverified`, not `verified_source`.

For general reviews, the adapter should first identify the likely legal domain,
then search the relevant Korean source family before claiming `verified_source`.

## Prompt Contract

The LLM system/developer prompt should include:

- The returned `kr_legal_review` workflow payload.
- The selected preset material, if any.
- The source status labels:
  - `verified_source`
  - `user_supplied_unverified`
  - `model_inference`
  - `requires_professional_review`
- The privacy fixture calibration pair only when using the `privacy` preset:
  - `tests/fixtures/kr_pipa_dpa_review/sample_vendor_dpa.md`
  - `tests/fixtures/kr_pipa_dpa_review/expected_review_skeleton.md`

## Output Contract

For the privacy preset, the adapter should request structured output matching:

```text
schemas/kr_pipa_dpa_review.schema.json
```

Minimum output fields:

- `verdict`
- `role_classification`
- `cross_border_status`
- `source_status`
- `required_gaps`
- `recommended_improvements`
- `source_log`
- `review_gate`

The `review_gate` must include `requires_professional_review`.

For the general workflow, the minimum output should include:

- `verdict`
- `issue_summary`
- `required_gaps`
- `recommended_next_steps`
- `source_log`
- `review_gate`

## Failure Rules

- No source lookup means no `verified_source` claim.
- No role facts means role classification must be `ambiguous` or equivalent.
- No overseas-transfer facts means cross-border status must be `unknown`.
- The adapter must not output "ready to sign" language.
- The adapter must not send, file, sign, or rely externally on the output.

## Minimal MCP Client Pseudocode

```text
source_plan = mcp.call("kr_legal_source_search", {
  "query": user_question,
  "live_lookup": false
})

review_payload = mcp.call("kr_legal_review", {
  "question": user_question,
  "document_text": document_text,
  "matter_context": matter_context,
  "preset": "general"
})

answer = llm.generate(
  system = "Use source status discipline. Do not provide final legal advice.",
  user = source_plan + review_payload
)

block_external_use_until_human_review(answer)
```
