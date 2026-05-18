# AGENTS.md - claude-for-legal-kr

This project inherits `~/vault/01_Projects/AGENTS.md`.

## Project Role

`claude-for-legal-kr` is a Korea-localized fork of
`anthropics/claude-for-legal`. Its job is to adapt legal workflow plugins to
Korean statutes, regulatory sources, drafting conventions, and professional
review gates.

It is not a legal-advice product. Every output remains a draft for qualified
attorney or responsible professional review.

## Module Responsibilities

| Area | Responsibility | Notes |
|---|---|---|
| `commercial-legal/` | Korea-facing contract review workflows | SaaS MSA, NDA, vendor terms, DPA-linked clauses |
| `privacy-legal/` | Korea privacy workflows | PIPA, data processing entrustment, cross-border transfer, incident response |
| `corporate-legal/` | Korea corporate and disclosure workflows | Commercial Act, FSC/FSS/DART-facing evidence, entity compliance |
| `regulatory-legal/` | Korea regulatory feed and gap workflows | Korean official sources first; no uncited regulatory claims |
| `ai-governance-legal/` | Korea AI governance workflows | AI vendor terms, internal AI use-case triage, policy gaps |
| `references/korea/` | Korea source catalog and playbook fragments | Keep source pointers, not copied confidential material |
| `docs/adr/` | Durable architecture decisions | Required for connector, naming, public interface, or plugin packaging decisions |
| `docs/implementation/` | Tactical plans and checklists | Keep implementation plans distinct from user-facing docs |

## External Source Boundary

Korean legal source retrieval should enter through explicit MCP connectors or
adapter documentation. Prefer `chrisryugj/korean-law-mcp` as a connector
dependency instead of copying its implementation into this repository.

Required source behavior:

- Cite Korean legal sources with source name, identifier, retrieval date, and
  whether the source was directly retrieved or inferred from supplied context.
- If the relevant Korean source was not retrieved, say so and mark the output as
  unverified.
- Do not present U.S. legal doctrines as Korean law without a jurisdiction gap
  warning.

## Localization Rules

Required:

- Preserve upstream Apache-2.0 notices and keep fork attribution visible.
- Keep `LICENSE` and upstream copyright headers intact.
- Use Korean drafting conventions for Korea-specific skills.
- Separate Korea-specific playbooks from upstream generic profiles.
- Keep examples synthetic; no client names, engagement names, fees, secrets, or
  privileged facts.

Forbidden:

- Committing API keys or live MCP credentials.
- Copying entire external repositories into this repo unless their license,
  attribution, and update strategy are documented in an ADR.
- Removing attorney/professional review gates from upstream skills.
- Publishing a skill that implies automated legal conclusions.

## Feature Addition Gate

Before changing a plugin or adding a Korea-specific skill:

1. Name the Korea-facing workflow being added.
2. Identify the controlling Korean source family, such as statutes,
   enforcement rules, regulator guidance, public notices, or case law.
3. Decide whether `korean-law-mcp` or another connector is required.
4. Define the output gate: draft only, review required, filing/send blocked.
5. Add or update tests, fixtures, or a documented manual verification checklist.

## Verification

Default narrow checks:

```bash
python3 -m compileall scripts
uv run --with pyyaml python scripts/lint-tool-scope.py
git status --short
```

For repository-level completion inside the vault, also run from `~/vault`:

```bash
./Harness/verify.sh
```
