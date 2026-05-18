# Korea Localization Roadmap

## Verdict

Conditional pass: the fork is viable if Korea localization is treated as
source-backed workflow design, not translation.

## Phase 0 - Workspace And Attribution

- [x] Create public GitHub fork: `capitalparser/claude-for-legal-kr`.
- [x] Clone into `~/vault/01_Projects/claude-for-legal-kr`.
- [x] Preserve upstream Apache-2.0 license and source history.
- [x] Add project-local guardrails, context, and ADR.

## Phase 1 - Source Connector Integration

- [x] Add `references/korea/source-catalog.md`.
- [x] Document `korean-law-mcp` install/configuration.
- [x] Define the connector response fields skills may rely on.
- [x] Add fixture examples for retrieved Korean statutes, cases, and regulator
      guidance.
- [x] Add API-key-gated `korean-law-mcp` live smoke script that skips safely
      until `LAW_OC` or `KOREAN_LAW_API_KEY` is set.
- [x] Extend the live smoke script to retrieve PIPA core articles after
      searching for `개인정보 보호법`.

## Phase 2 - First Plugin Wedge

Recommended first wedge:

1. `privacy-legal` PIPA/DPA review, because source authority and business value
   are clear.
2. `commercial-legal` SaaS MSA/NDA vendor review, because it pairs naturally
   with privacy and AI vendor terms.
3. `regulatory-legal` Korea source watcher, because it proves the MCP boundary.

## Phase 3 - Publication Quality

- [ ] Rename or add Korea-specific marketplace entries only after plugin naming
      and compatibility are tested.
- [ ] Add a Korea-specific README section with disclaimers and setup.
- [ ] Run repository validation and manual plugin install smoke tests.
- [ ] Publish status as experimental until source-backed citation checks pass.

## Required Gap Classification

Required gaps:

- Live `korean-law-mcp` smoke test has not been run with a real Law.go.kr OC
  key in this Codex session; the user shell has reported successful PIPA search,
  and the next run should confirm core article retrieval.
- No plugin install smoke test yet.

Recommended gaps:

- Decide whether repository stays a broad fork or narrows to a smaller
  `korea-legal-workbench` plugin set.
- Add Korean output templates for legal memo, contract issue list, and
  regulator gap memo.
