# General Korean Legal Review Workflow

Purpose: help a legal non-specialist, company operator, or individual prepare a
clear issue memo before asking counsel or relying on a decision.

This workflow is not legal advice. It is a structured first-pass review that
separates facts, source lookups, model inference, and professional review gates.

## Inputs

- User question or business situation
- Optional document or clause text
- Optional matter context: parties, transaction, jurisdiction, timeline, use case
- Optional source results from Korean statutes, regulations, guidance, or cases

## Review Steps

1. Restate the issue in plain Korean.
2. Identify likely legal domains and Korean source families to check.
3. Separate known facts from missing facts.
4. Mark source status for every legal proposition:
   - `verified_source`
   - `user_supplied_unverified`
   - `model_inference`
5. Classify gaps:
   - `required_gaps`: blocks reliance or escalation.
   - `recommended_next_steps`: useful but not blocking.
6. End with `requires_professional_review` before external reliance.

## Output Shape

```text
Verdict: pass / conditional / fail / unknown

Issue summary:
- Plain Korean summary of what matters.

Likely source families:
- Statute / enforcement decree / regulator guidance / case law / contract.

Required gaps:
- Facts, documents, or source lookups that must be resolved.

Recommended next steps:
- Practical actions for the business user.

Source log:
- Source name, identifier, retrieval status, and source_status.

Review gate:
- requires_professional_review
```

## Safety Rules

- Do not present the answer as a final legal opinion.
- Do not say "safe to sign", "legally compliant", or "ready to file" without
  professional review.
- If the law was not retrieved, say what must be checked.
- If the facts are incomplete, make the uncertainty visible.
