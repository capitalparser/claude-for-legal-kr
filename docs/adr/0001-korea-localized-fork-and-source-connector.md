# ADR 0001: Korea-Localized Fork And Source Connector Boundary

- Status: Accepted
- Date: 2026-05-18

## Context

`anthropics/claude-for-legal` provides legal workflow plugins, skills, agents,
and connector documentation. Its default assumptions, examples, connectors, and
legal doctrines are U.S. or global-enterprise oriented.

`chrisryugj/korean-law-mcp` provides MCP access to Korean legal sources and is a
natural source connector for Korea-facing legal workflows.

## Decision

Create `capitalparser/claude-for-legal-kr` as a public GitHub fork of
`anthropics/claude-for-legal`.

Keep `korean-law-mcp` as an external connector dependency and integration
target, not vendored source code, until there is a specific reason to copy code.

Korea localization will begin through project documentation, source catalogs,
and additive Korea-specific playbook/skill changes before any broad rewrite of
upstream plugins.

## Consequences

Positive:

- Upstream attribution and diff history stay clear.
- The fork can receive upstream improvements.
- `korean-law-mcp` can evolve independently.
- Legal-source retrieval remains an explicit external boundary.

Tradeoffs:

- Users must install/configure the Korean law MCP separately.
- Tests need fakes or fixtures for connector responses.
- Some upstream language will remain U.S.-centric until each plugin is
  deliberately localized.

## Required Follow-Up

- Add a Korea source catalog under `references/korea/`.
- Add installation notes for using the fork with `korean-law-mcp`.
- Choose the first plugin wedge and write a targeted implementation plan.
- Add tests or fixture checks around citation and review-gate behavior before
  publishing Korea-specific skills as ready.

