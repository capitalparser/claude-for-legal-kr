# Korea Source Catalog

This catalog defines the preferred Korean source families for localized legal
workflows. It is an integration guide, not a copied legal database.

## Connector Priority

Primary connector target:

- `chrisryugj/korean-law-mcp`

Connector responses should preserve enough metadata for a skill to distinguish
direct retrieval from model inference.

Required metadata:

- source family,
- title,
- source identifier or URL,
- effective date or publication date when available,
- retrieval date,
- excerpt or structured fields used by the skill.

## Source Families

| Family | Use | Notes |
|---|---|---|
| Korean statutes and enforcement decrees/rules | Controlling legal basis | Prefer official current text before summaries |
| Supreme Court and lower-court cases | Case-law support | Mark case-law search gaps explicitly |
| Regulator guidance and notices | Compliance and enforcement posture | Include agency and publication date |
| FSC/FSS/DART disclosures | Corporate, finance, audit, and disclosure workflows | Use DART for company-specific public evidence |
| PIPC guidance | Privacy and data protection workflows | Use for PIPA interpretation, incidents, cross-border transfer, entrustment |
| KFTC materials | Competition, platform, advertising, and terms review | Distinguish statute from policy guidance |
| MOEL materials | Employment workflows | Distinguish statutes, administrative interpretations, and guidance |
| KIPO/KIPRIS materials | IP workflows | Use for trademark/patent search support, not legal conclusions |

## Output Labels

Use these labels in Korea-facing skills:

- `verified_source`: retrieved in the current workflow.
- `user_supplied_unverified`: supplied by user but not independently retrieved.
- `model_inference`: inferred without retrieval; requires explicit gap warning.
- `requires_professional_review`: cannot be used externally without review.

## Open Questions

- Exact MCP tool names and response schema from `korean-law-mcp`.
- Whether official Korean sources require API keys or rate-limit handling.
- Which source families should be fixture-tested first.

