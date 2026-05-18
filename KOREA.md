# Claude For Legal KR

This fork adapts `anthropics/claude-for-legal` for Korea-facing legal,
regulatory, privacy, corporate, commercial contract, and AI governance
workflows.

## Status

Experimental. The repository has been forked and the Korea localization
workspace is being prepared. Do not rely on current plugin outputs as Korean
legal conclusions.

## Source Strategy

Korea-specific legal retrieval should be handled through explicit MCP
connectors. The first target connector is:

- `chrisryugj/korean-law-mcp`

The preferred integration model is dependency/configuration, not copying the
connector source into this repository.

## Review Gate

Every output is a draft for qualified human review. Korea-facing outputs must
state:

- jurisdiction assumptions,
- retrieved source basis,
- unverified gaps,
- required reviewer action before use.

## Attribution

This repository is a fork of `anthropics/claude-for-legal`, licensed under
Apache-2.0. Upstream notices and license terms are preserved.

