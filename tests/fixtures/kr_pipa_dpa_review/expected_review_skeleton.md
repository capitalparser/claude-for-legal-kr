# Expected KR PIPA/DPA Review Skeleton

This is a deterministic expected shape for the synthetic fixture, not legal
advice.

**Verdict: conditional**
**Role classification:** 처리위탁 with 제3자 제공 risk requiring facts.
**Cross-border status:** 국외 이전 identified.
**source status:** verified_source for live PIPA lookups when available;
model_inference where live MCP is unavailable.
**Review gate:** requires_professional_review

## required gaps

| Gap | PIPA anchor | Why |
|---|---|---|
| AI training and broad service improvement purposes are not separated from entrusted processing | 제26조 | Processing purpose/scope may exceed 처리위탁 |
| Subprocessor appointment lacks prior notice/approval structure | 제26조 | Re-entrustment and supervision gap |
| Overseas transfer fields are generic and website-updatable | 제28조의8 | Recipient/country/items/purpose/period/safeguards not fixed |
| Breach notification waits until internal investigation completion | 제34조 | Controller may not have enough time for Korean incident response |
| Security measures are generic | 제29조 | No specific technical/managerial/physical safeguards |

## recommended improvements

- Add Korea PIPA addendum.
- Freeze subprocessors in an exhibit or provide advance change notice.
- Separate AI training, telemetry, analytics, and service improvement.
- Add deletion certification and backup retention limits.

## source status

- 제26조: verified_source when `korean-law-mcp` live lookup succeeds.
- 제28조의8: verified_source when `korean-law-mcp` live lookup succeeds.
- 제29조: verified_source when `korean-law-mcp` live lookup succeeds.
- 제34조: verified_source when `korean-law-mcp` live lookup succeeds.
