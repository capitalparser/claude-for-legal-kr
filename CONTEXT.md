# CONTEXT.md - claude-for-legal-kr

## Purpose

Create a Korea-localized legal workflow plugin pack based on
`anthropics/claude-for-legal`, with official Korean legal source retrieval
provided through MCP connectors such as `chrisryugj/korean-law-mcp`.

The first useful product shape is not a general Korean lawyer replacement. It
is a Korea corporate, regulatory, privacy, AI governance, and commercial
contract review workbench that produces cited drafts, issue lists, and
professional-review memos.

## Users

- In-house legal or compliance teams operating in Korea.
- Finance, audit, and corporate governance professionals preparing issue lists
  for legal review.
- Builders who need Korean regulatory source retrieval inside agent workflows.

## Non-Goals

- No legal advice automation.
- No court filing, notice sending, regulator submission, or client-facing letter
  without an explicit human review gate.
- No confidential client data in fixtures or examples.
- No wholesale vendoring of `korean-law-mcp` until an ADR justifies it.
- No claim that Anthropic, Claude, or the upstream project endorses this fork.

## Ubiquitous Language

- Korea source connector: MCP server or explicit adapter that retrieves Korean
  legal sources and returns source metadata.
- Verified citation: citation backed by retrieved source text or metadata in the
  current workflow.
- Unverified citation: citation supplied by the user or inferred by the model
  without retrieval evidence.
- Review gate: point where the workflow must stop until a qualified human
  reviewer approves draft use.
- Korea playbook: local policy, clause standard, risk calibration, and output
  template for Korea-facing work.

## Source Priority

1. Official Korean legal and regulatory sources.
2. Public regulator guidance and press releases.
3. Public company filings and DART disclosures where corporate or disclosure
   facts are relevant.
4. User-supplied documents, clearly labeled as supplied and unverified against
   official sources unless separately retrieved.
5. Secondary sources only as background, never as controlling authority.

## Initial Wedge

Start with Korea localization for:

- `privacy-legal`: PIPA, DPA, PIA, DSAR-like data subject request workflows.
- `commercial-legal`: SaaS MSA, NDA, vendor AI/data clauses.
- `regulatory-legal`: official-source watcher and gap memo.
- `ai-governance-legal`: AI use-case and vendor AI review against Korea-facing
  governance obligations and emerging guidance.
- `corporate-legal`: Commercial Act, DART/FSC/FSS-facing corporate evidence
  and disclosure support.

## Invariants

- Draft outputs must disclose jurisdiction assumptions.
- Legal claims must distinguish verified source retrieval from model inference.
- Korean localization should be additive until replacement behavior is
  explicitly tested.
- Upstream attribution and license notices stay visible.

