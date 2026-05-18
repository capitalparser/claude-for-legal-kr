# Korea PIPA/DPA Review Playbook

This reference supports `/privacy-legal:kr-pipa-dpa-review`.

It is a review playbook, not legal advice. It identifies issues the skill must
surface before a Korean attorney or responsible privacy professional reviews
the final output.

## Source Baseline

Use official Korean sources first:

- Law.go.kr current text for 개인정보 보호법.
- Law.go.kr standard personal information processing entrustment agreement.
- `korean-law-mcp` citation verification where available.
- Korean case law for 처리위탁 vs 제3자 제공 role classification.
- PIPC guidance where available for privacy-policy, overseas-transfer, and
  incident-response interpretation.

## Review Matrix

| Area | Check | Classification |
|---|---|---|
| 처리위탁 document terms | Purpose/scope, period, re-entrustment, security, supervision, deletion/return, liability | required gaps if absent |
| 제3자 제공 risk | Recipient has independent purpose, independent benefit, weak controller supervision, or marketing/training use | required gaps; may be fail |
| 국외 이전 | Recipient/country/items/purpose/period/safeguards/legal basis clear | required gaps if missing |
| Security | Technical, managerial, and physical safeguards are specific enough | required gaps if generic |
| Breach notice | Notice timing and content allow Korean controller response | required gaps if absent/vague |
| Privacy policy consistency | Entrustment and overseas-transfer facts align with public policy | recommended improvements or required gaps |
| AI vendor overlay | Training, model improvement, telemetry, evaluation, and abuse-monitoring purposes separated | required gaps if uncontrolled |

## Article Anchors

- 제26조: processing entrustment / 개인정보 처리위탁.
- 제28조의8: overseas transfer / 개인정보 국외 이전.
- 제29조: safety measures.
- 제30조: privacy policy.
- 제34조: leak/breach notification.

## Default Verdict Rules

- `pass`: no required gaps after source-backed review; professional review still
  required.
- `conditional`: required gaps are fixable through amendments or facts.
- `fail`: 제3자 제공 is disguised as 처리위탁, overseas transfer basis is absent,
  AI training use is uncontrolled, or core 제26조 terms are missing.

## Output Requirements

The review must include:

- `pass / conditional / fail` verdict.
- `required gaps` table.
- recommended improvements table.
- source status labels.
- role classification.
- 국외 이전 status.
- review gate marked `requires_professional_review`.

## Source Status Labels

- `verified_source`: retrieved or verified in the current workflow.
- `user_supplied_unverified`: supplied by user but not checked.
- `model_inference`: inferred without source retrieval.
- `requires_professional_review`: external use blocked pending review.

