# Generic LLM Adapter Contract

## Purpose

This document defines what is needed to use `claude-for-legal-kr` outside
Claude Code, for example in OpenAI, ChatGPT Apps, LangChain, a custom agent
runtime, or another MCP-capable LLM client.

The core idea:

1. Use `korean-law-mcp` as the source retrieval tool.
2. Use the KR PIPA/DPA review skill as the workflow prompt.
3. Validate the output against `schemas/kr_pipa_dpa_review.schema.json`.

## Required Inputs

- `document_text`: the DPA, contract excerpt, or vendor data-processing terms.
- `matter_context`: optional facts such as controller/processor roles, data
  categories, Korean data subjects, overseas processing, and AI usage.
- `source_results`: results returned by `korean-law-mcp` or another Korean legal
  source connector.

## Required Tool Sequence

The adapter should run this tool sequence before the final review:

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

## Prompt Contract

The LLM system/developer prompt should include:

- The content of `privacy-legal/skills/kr-pipa-dpa-review/SKILL.md`.
- The Korea PIPA/DPA playbook at
  `privacy-legal/references/korea-pipa-dpa-playbook.md`.
- The source status labels:
  - `verified_source`
  - `user_supplied_unverified`
  - `model_inference`
  - `requires_professional_review`
- The fixture calibration pair:
  - `tests/fixtures/kr_pipa_dpa_review/sample_vendor_dpa.md`
  - `tests/fixtures/kr_pipa_dpa_review/expected_review_skeleton.md`

## Output Contract

The adapter should request structured output matching:

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

## Failure Rules

- No source lookup means no `verified_source` claim.
- No role facts means role classification must be `ambiguous` or equivalent.
- No overseas-transfer facts means cross-border status must be `unknown`.
- The adapter must not output "ready to sign" language.
- The adapter must not send, file, sign, or rely externally on the output.

## Minimal Adapter Pseudocode

```text
document_text = load_user_document()
source_results = korean_law_mcp.lookup([
  "개인정보 보호법 제26조",
  "개인정보 보호법 제28조의8",
  "개인정보 보호법 제29조",
  "개인정보 보호법 제34조",
])

review = llm.generate(
  system = kr_pipa_dpa_review_skill + korea_playbook,
  user = document_text + matter_context + source_results,
  response_schema = schemas/kr_pipa_dpa_review.schema.json,
)

validate(review)
block_external_use_until_human_review(review)
```

