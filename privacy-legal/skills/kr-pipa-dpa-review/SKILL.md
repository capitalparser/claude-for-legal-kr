---
name: kr-pipa-dpa-review
description: >
  Korea PIPA review for a DPA, data processing entrustment agreement, vendor
  privacy addendum, SaaS data clause, or AI/vendor data-processing terms. Use
  when the user asks whether a DPA is acceptable for Korea, mentions PIPA,
  개인정보 보호법, 처리위탁, 수탁자, 개인정보 국외 이전, or attaches Korean
  privacy/data-processing terms.
argument-hint: "[file | Drive link | paste text | contract excerpt]"
---

# /kr-pipa-dpa-review

Review a DPA or privacy/data-processing clause under Korea's Personal
Information Protection Act (PIPA, 개인정보 보호법). This is a Korea-localized
review workflow, not a translation of `/privacy-legal:dpa-review`.

Every output is a draft for qualified attorney or responsible professional
review. Do not tell the user a contract is ready to sign, send, file, or rely on
externally unless the review gate is satisfied.

## Pre-flight

1. Load `~/.claude/plugins/config/claude-for-legal/privacy-legal/CLAUDE.md` if
   available. Use it for house style, outputs folder, reviewer header, and
   privacy-policy commitments. If absent, continue with the default Korea
   review template and say the local playbook was not loaded.
2. Load this repository's Korea source catalog:
   `references/korea/source-catalog.md`.
3. Check whether `korean-law-mcp` is available. Prefer it for Korean legal
   source retrieval and citation verification.
4. If no Korean source connector is available, continue only as a draft issue
   spotter and label legal-source statements as `model_inference` or
   `user_supplied_unverified`.
5. Ask for missing context only if it changes classification:
   - controller/client/company role,
   - processor/vendor role,
   - data categories,
   - whether data subjects include Korea residents,
   - whether data leaves Korea,
   - whether the vendor may use data for AI training, analytics, or service
     improvement.

## Source Retrieval Contract

Use `korean-law-mcp` or another configured Korea source connector to retrieve
or verify, at minimum:

- 개인정보 보호법 제26조: processing entrustment / 처리위탁.
- 개인정보 보호법 제28조의8: overseas transfer / 개인정보 국외 이전.
- 개인정보 보호법 제29조 and related safety-measure rules: security controls.
- 개인정보 보호법 제30조: privacy policy disclosure items, if policy
  consistency is in scope.
- 개인정보 보호법 제34조: leak/breach notification, if incident terms are in
  scope.
- Official standard personal information processing entrustment agreement
  published through law.go.kr, when reviewing mandatory entrustment clauses.
- Case law distinguishing 처리위탁 from 제3자 제공 when role classification is
  disputed.

For each source-sensitive statement, tag the basis:

- `verified_source`: retrieved in the current workflow.
- `user_supplied_unverified`: supplied by user but not independently retrieved.
- `model_inference`: inferred without retrieval; requires explicit gap warning.
- `requires_professional_review`: cannot be used externally without review.

If `korean-law-mcp` returns `[NOT_FOUND]`, `[HALLUCINATION_DETECTED]`, an empty
result, or a tool error, do not fill the gap from memory. Report the failed
lookup and mark the affected issue as unverified.

## Classification

Before term review, classify the data transfer:

| Classification | Test | Consequence |
|---|---|---|
| 처리위탁 | Vendor processes personal information for the controller's work and benefit, under controller supervision | PIPA entrustment document, supervision, disclosure, and flow-down checks apply |
| 제3자 제공 | Recipient uses personal information for its own business purpose or independent benefit | Consent/notice/legal-basis issues may apply; a DPA may not cure the structure |
| 공동/독립 처리 ambiguity | Both parties determine meaningful purposes or the documents conflict | Mark conditional/fail until facts and outside counsel review resolve the role |
| 국외 이전 | Personal information is transferred, accessed, stored, or processed outside Korea | PIPA overseas transfer basis, notice/disclosure, recipient/country/items/retention/safeguards checks apply |

Use the Korean Supreme Court role-classification factors where retrieved:
purpose of acquisition, method, consideration, real supervision, data-subject
impact, and who substantively needs the data.

## Core PIPA/DPA Checks

Check every agreement against these items:

| Term | Korea review question | Default severity if missing |
|---|---|---|
| Purpose and scope | Does the DPA identify the entrusted processing purpose and scope? | required gaps |
| Entrustment period | Is the processing/entrustment period defined? | required gaps |
| Re-entrustment / subprocessors | Is prior approval or notice/consultation for subprocessors defined? | required gaps |
| Purpose limitation | Does the vendor avoid use beyond entrusted work, including AI training, analytics, resale, or unrelated service improvement? | required gaps |
| Third-party disclosure | Could any transfer be 제3자 제공 rather than 처리위탁? | required gaps |
| Security measures | Are technical, managerial, and physical safeguards specific enough? | required gaps |
| Supervision and audit | Can the controller inspect, supervise, and require correction? | required gaps |
| Deletion/return | Are return, deletion, backup carveouts, certification, and timing stated? | required gaps |
| Data subject rights support | Does the vendor support access, correction, deletion, suspension, and complaint handling where relevant? | recommended improvements or required gaps depending on role |
| Breach notification | Does notice timing let the controller satisfy Korean incident duties? | required gaps |
| Overseas transfer | Are country, recipient, items, purpose, period, safeguards, and legal basis clear? | required gaps |
| Privacy policy consistency | Does the privacy policy disclose entrustment and overseas-transfer facts consistently? | recommended improvements or required gaps |
| Liability and indemnity | Does responsibility for vendor-caused violations align with the risk and MSA cap? | recommended improvements |

## AI Vendor Overlay

If the vendor offers AI, analytics, model improvement, telemetry, or automated
decisioning:

- Treat training, fine-tuning, evaluation, and abuse-monitoring clauses as
  separate processing purposes.
- Flag any clause that allows vendor model training or broad service
  improvement on customer personal information.
- Ask whether de-identification, pseudonymization, or anonymization is actually
  used; do not accept labels without operational support.
- Require source status for any claim about pseudonymous information,
  anonymized data, or exceptions.

## Output Format

Write in Korean unless the user asks otherwise. Use verdict-first format:

```markdown
[WORK-PRODUCT HEADER if configured]

# KR PIPA/DPA Review: [counterparty or document name]

**Verdict:** [pass / conditional / fail]
**Role classification:** [처리위탁 / 제3자 제공 risk / ambiguous]
**Cross-border status:** [none identified / 국외 이전 identified / unknown]
**Source status:** [verified_source summary | user_supplied_unverified | model_inference]
**Review gate:** requires_professional_review

## Bottom Line

[2-4 sentences. Can this move forward, and what must change first?]

## Required Gaps

| # | Gap | Why it matters under PIPA | Source status | Proposed fix |
|---|---|---|---|---|

## Recommended Improvements

| # | Improvement | Benefit | Source status | Proposed wording or action |
|---|---|---|---|---|

## Role And Transfer Analysis

[Explain 처리위탁 vs 제3자 제공 and 국외 이전 facts. If ambiguous, say exactly what fact would resolve it.]

## Clause Review

[Term-by-term review. Keep each item short: document says / PIPA issue / fix.]

## Source Log

| Source | Identifier / URL | Retrieved? | Used for |
|---|---|---|---|

## Attorney / Professional Review Gate

This output is a draft. A qualified attorney or responsible professional must
verify sources, role classification, cross-border transfer basis, and final
wording before the document is signed, sent, filed, or relied on externally.
```

## Verdict Rules

- `pass`: no required gaps after source-backed review; still requires final
  reviewer sign-off.
- `conditional`: gaps exist but appear fixable with targeted amendments or
  facts.
- `fail`: role classification is wrong, 제3자 제공 is disguised as 처리위탁,
  overseas transfer basis is absent, AI training use is uncontrolled, or a
  core PIPA entrustment term is missing.

## What This Skill Does Not Do

- It does not provide legal advice.
- It does not decide whether a company should sign.
- It does not replace official source retrieval.
- It does not draft a full DPA from scratch unless the user separately asks for
  drafting after the review.
- It does not treat U.S., GDPR, or global DPA language as sufficient for Korea
  without Korea-specific source checks.

