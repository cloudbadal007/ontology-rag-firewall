# SHACL Rules Explained

This document translates each SHACL constraint into plain language for legal,
procurement, finance, and platform engineering teams.

## Severity Model

- `⚠️ Warning`: contract may proceed only after explicit human review.
- `🚨 Violation`: contract should be blocked and escalated.

## Rule-by-Rule Interpretation

1) **LiabilityCapRatioShape** (`⚠️`)
- Trigger: Liability cap is less than 10% of contract value.
- Risk: Disproportionate downside exposure for buyer.
- Action: Route to legal for risk acceptance or renegotiation.

2) **DirectDamagesReviewShape** (`⚠️`)
- Trigger: Liability scope is `DirectDamagesOnly` and no human review marker.
- Risk: Consequential damages are excluded, reducing real recoverability.
- Action: Require explicit legal acceptance of reduced coverage.

3) **PaymentTermShape** (`⚠️`)
- Trigger: Payment terms exceed 60 days.
- Risk: Cash flow impact and working-capital pressure.
- Action: Finance review and exception approval.

4) **TerminationNoticeShape** (`⚠️`)
- Trigger: Notice period is below 30 days.
- Risk: Insufficient operational runway for transition.
- Action: Legal and operational continuity review.

5) **SLACommitmentShape** (`⚠️`)
- Trigger: Uptime commitment is below 99.5%.
- Risk: Reliability target may be insufficient for business continuity.
- Action: Validate alignment with service criticality tier.

6) **LowConfidenceExtractionShape** (`⚠️`)
- Trigger: Extraction confidence is below 0.75.
- Risk: Parsed semantics may be unreliable.
- Action: Force manual verification of extracted fields.

7) **NoRemedySLAShape** (`⚠️`)
- Trigger: SLA remedy is `NoRemedy` (commercially reasonable efforts only).
- Risk: No enforceable consequence for poor performance.
- Action: Require enforceable credits/financial remedy/termination right.

8) **AutoRenewalFlagShape** (`⚠️`)
- Trigger: Auto-renew is enabled and cancellation notice is under 60 days.
- Risk: Easy accidental renewal with limited off-ramp.
- Action: Procurement controls + calendar/notification safeguards.

9) **MissingLiabilityClauseShape** (`🚨`)
- Trigger: No liability clause extracted from contract graph.
- Risk: Core legal protection missing or extraction failure on a critical section.
- Action: Block approval until liability terms are confirmed.

10) **HighValueLowCapShape** (`🚨`)
- Trigger: Contract value > $1M and liability cap < $100K.
- Risk: Large commercial exposure with very low absolute recourse.
- Action: Immediate legal escalation.

## Operational Guidance

- Treat warning outcomes as non-automatable unless risk policy says otherwise.
- Treat critical outcomes as hard blocks.
- Maintain auditable evidence of each violation and reviewer decision.
