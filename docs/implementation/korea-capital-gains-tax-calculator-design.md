# Korea Capital Gains Tax Calculator Design

## Verdict

Status: `draft`

Build a Korea-facing capital gains tax workbench for non-tax specialists, starting
with residential real estate. The product must classify both the disposed asset
and other household-held real estate before it calculates tax.

This is not a tax-advice automation product. Every result is an estimate for
professional review, with source basis, unresolved facts, and review gates shown
next to the calculation.

## Scope

### MVP

- Residential real estate capital gains tax only.
- Disposed asset classification: apartment, detached house, row/multi-family
  house, officetel, mixed-use building, right to acquire housing, occupancy
  right, or unknown.
- Other household-held real estate classification for house-count purposes.
- Household house-count result: likely one-household one-house, temporary
  two-house candidate, multi-house candidate, or indeterminate.
- Core calculation scaffold: transfer value, acquisition value, necessary
  expenses, gain, long-term holding deduction candidate, basic deduction,
  taxable base, income tax, local income tax, total estimated tax.
- Evidence panel with official-source links and retrieval metadata.

### Out of Scope for MVP

- Stock, overseas stock, unlisted stock, virtual assets, pure land, and business
  transfer calculations.
- Final filing forms and HomeTax submission.
- Automated legal or tax conclusions without professional review.
- Live scraper behavior inside domain modules.

## Product Principle

The user should not be asked "How many houses do you own?" because that pushes a
tax-law conclusion onto a non-specialist. The UI asks the user to list household
real estate, then the system classifies whether each item is likely counted as a
house for the relevant tax judgment.

## Domain Model

### Disposed Asset

The property being sold. It has transfer price, acquisition price, acquisition
date, transfer date, residence period, holding period, and asset-type facts.

### Household Property

A property held by the taxpayer, spouse, or household member. The disposed asset
is also part of the household property set, but the UI keeps it visually
separate because it drives the tax base.

### House-Count Classification

Each household property gets a classification:

- `included`: likely included in house count.
- `excluded`: likely excluded from house count.
- `candidate`: may be included depending on missing facts.
- `unknown`: facts are insufficient.

The result stores explanation, required facts, confidence, and source IDs.

### Evidence Source

Each rule links to an evidence source record:

- `id`
- `source_name`
- `source_type`
- `url`
- `retrieved_at`
- `effective_date`
- `citation_label`
- `summary`
- `verified`

## UX Flow

1. Start with a verdict-first header: "draft estimate", source date, and review
   gate.
2. Ask what is being sold.
3. Ask facts that determine whether the disposed asset is treated as a house.
4. Ask the user to add other household-held real estate one by one.
5. For each property, show a small classification card:
   - likely house-count status,
   - why it was classified that way,
   - missing facts,
   - source link.
6. Show household classification before tax:
   - one-household one-house candidate,
   - temporary two-house candidate,
   - multi-house candidate,
   - indeterminate.
7. Only then show tax estimate and gap classification.

## UI Requirements

- Follow PAS Workbench design kit: Pretendard, body letter-spacing `-0.02em`,
  body line-height `1.6`, tokenized colors, verdict-first header, KPI strip,
  evidence table, and explicit gap classification.
- The first viewport must show asset status, household house-count status, and
  estimate status.
- Avoid marketing hero layout. This is a workbench.
- Use compact controls and cards. Do not nest cards inside cards.
- Mobile layout must keep the property list editable without horizontal text
  overlap.

## Source Strategy

Primary source families:

- National Tax Service "Easy Capital Gains Tax" page:
  https://www.nts.go.kr/tax/yangdo_2.html
- National Tax Service long-term holding deduction page:
  https://nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7697&mi=2311
- National Law Information Center for Income Tax Act and subordinate law:
  https://www.law.go.kr
- National Tax Law Information System for rulings, precedents, and tax tribunal
  decisions:
  https://txsi.hometax.go.kr
- Korean Law MCP as source connector candidate:
  https://github.com/chrisryugj/korean-law-mcp

The design follows the legal connector principles in `anthropics/claude-for-legal`:
read-heavy tools, source provenance, citation-ready identifiers, and no
instruction-like content treated as commands.

## Architecture

### Domain Modules

- `assetClassifier`: classifies disposed asset and other household properties.
- `householdClassifier`: aggregates household property classifications into a
  household house-count judgment.
- `periodCalculator`: calculates holding and residence periods.
- `taxCalculator`: performs deterministic arithmetic from trusted input.
- `gapClassifier`: separates blocking missing facts from confidence-improving
  facts.

Domain modules must be deterministic and must not call network, filesystem,
browser, subprocess, database, or LLM APIs.

### Adapter Modules

- `evidenceRepository`: reads local mock evidence JSON in MVP.
- `koreanLawMcpClient`: later adapter for Korean Law MCP.
- `ntsSourceClient`: later adapter for National Tax Service source retrieval if
  Korean Law MCP does not cover tax guidance sufficiently.

### Presentation

- Single-file HTML prototype first.
- If the prototype hardens into a project app, split into `src/domain`,
  `src/evidence`, and `src/ui`.

## Risk Controls

- Every result must be marked `draft`.
- If any house-count property is `candidate` or `unknown`, tax result status is
  `conditional`.
- If source evidence is mock or not retrieved during the current session, mark
  citations as `unverified`.
- No personal information, real addresses, or client facts in fixtures.

## Test Fixtures

Minimum fixture set:

- One disposed apartment, no other properties.
- Disposed apartment plus spouse-owned officetel with unknown actual use.
- Disposed house plus temporary two-house candidate.
- Disposed house plus inherited house candidate.
- Mixed-use building where residential/commercial split is unknown.
- Officetel disposed asset with residential use facts missing.

## Open Gaps

### Required

- Confirm current law snapshot date before production use.
- Confirm which official source will be authoritative for tax-specific guidance
  not covered by National Law Information Center.
- Define exact MVP formula boundaries for high-priced one-house cases and
  long-term holding deduction.

### Recommended

- Compare representative cases against HomeTax simulation results.
- Add a source refresh checklist before each tax-year update.
- Add exportable review memo for tax professional handoff.

