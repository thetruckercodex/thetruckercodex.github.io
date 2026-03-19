---
layout: post
title: "Violation Severity Weights: Why Some Tickets Cost You More CSA Points"
date: 2026-03-19
categories: audits-violations
description: "Enforcement intelligence analysis: Violation Severity Weights: Why Some Tickets Cost You More CSA Points. Data-driven insights from FMCSA and CVSA records for motor carriers and compliance professionals."
---

Not all roadside violations hit your CSA score equally. A driver cited for an inoperable headlamp (393.9) walks away with a severity weight of 2. A driver placed out of service for a brake hose or tubing chafing violation (393.45) generates a severity weight of 8 — before time-weighting or inspection multipliers are applied. That gap is not arbitrary. It is a calculated enforcement signal, and understanding it is the difference between managing your SMS profile strategically and reacting to it blindly.

## How CSA Violation Severity Weights Work

The FMCSA's Safety Measurement System assigns every roadside violation a severity weight on a scale from 1 to 10. These weights are defined in the [FMCSA SMS Methodology Document](https://ai.fmcsa.dot.gov/SMS/Tools/Downloads/SMSMethodology.aspx) and reflect the statistical relationship between a given violation type and crash risk. Higher weights correspond to violations that FMCSA's predictive modeling has identified as more strongly correlated with accident involvement.

Raw severity weights are just the starting point. The SMS then applies three additional multipliers before producing a carrier's BASIC score:

- **Time weight**: Violations from the most recent 6 months carry a multiplier of 3; months 7–12 carry a multiplier of 2; months 13–24 carry a multiplier of 1.
- **Out-of-service weight**: Any violation that resulted in an OOS order receives an additional severity bump — typically doubling the impact in the Unsafe Driving and Vehicle Maintenance BASICs.
- **Inspection weight**: The total is normalized against the number of inspections to produce a per-inspection average, then compared against peer carriers of similar size.

This layered calculation means a single high-severity OOS violation in the past six months can be mathematically equivalent to four or five lower-severity non-OOS violations from a year ago.

### The BASIC Distribution That Actually Matters

Severity weights are applied independently within each of the seven BASICs: Unsafe Driving, Hours-of-Service Compliance, Driver Fitness, Controlled Substances/Alcohol, Vehicle Maintenance, Hazardous Materials Compliance, and Crash Indicator. Carriers that focus only on their worst-performing BASIC often miss the compound damage occurring across multiple BASICs simultaneously. If you haven't done a structured review using your SMS scorecard, the analysis in [how to read your CSA scorecard and identify your biggest risks](https://blog.thetruckercodex.com/how-to-read-your-csa-scorecard-and-identify-your-biggest-ris/) lays out a practical framework for cross-BASIC triage.

## High-Severity Violations by BASIC Category

### Vehicle Maintenance: Where the Heaviest Weights Concentrate

The Vehicle Maintenance BASIC contains the largest number of severity weight 8–10 violations in the SMS violation table. Brake system defects dominate this tier:

- **393.45 — Brake hose or tubing chafing or kinking** (Severity: 8, OOS-eligible)
- **393.48(a) — Brakes not maintaining adjustment limits** (Severity: 8, OOS-eligible)
- **393.52 — Brake performance: insufficient stopping force** (Severity: 10)
- **393.9 — Inoperable required lamps** (Severity: 2–4, depending on lamp type)
- **393.75(a) — Tire tread depth below federal minimum** (Severity: 8, OOS-eligible when below 2/32")

The difference between a severity 2 and severity 8 violation within the same BASIC can be the determining factor in whether a carrier crosses an intervention threshold. FMCSA's [public safety data portal](https://www.fmcsa.dot.gov/safety/data-and-statistics) shows Vehicle Maintenance consistently as the highest-volume BASIC for OOS violations across North American roadside inspections.

### Unsafe Driving: Low Volume, Extreme Weight

The Unsafe Driving BASIC operates differently from Vehicle Maintenance in one critical respect — the violation volume is typically lower, but the severity weights are among the highest in the entire system. Speeding 15+ mph over the posted limit (§392.6 enforcement) carries a severity weight of 10. Reckless driving violations under §392.2 can carry weights of 9–10 depending on state-level citation coding. A single speeding ticket at 15+ over in the most recent six-month window, multiplied by the time weight of 3 and an OOS multiplier if applicable, can single-handedly push a carrier into the alert threshold.

This is precisely why roadside enforcement patterns — not just the violation itself — determine SMS outcomes. Understanding [what triggers a compliance review](https://blog.thetruckercodex.com/how-fmcsa-selects-carriers-for-compliance-reviews-the-data-b/) begins with understanding which violations in which BASICs are generating the algorithmic flags that elevate carrier risk scores.

### Hours of Service: The Hidden Severity Trap

HOS violations that appear administrative on their face often carry severity weights that operators underestimate. A Form and Manner violation (§395.8(e)) carries a severity weight of 1. But a falsification of records violation (§395.8(e)(1)) — which is a different citation even if issued for what looks like the same logbook problem — carries a severity weight of 10 and is OOS-eligible. The distinction comes down to inspector determination of intent, and that determination has enormous CSA consequences. Carriers dealing with driver log issues should cross-reference the violation patterns documented in [common DOT violations and how to avoid them](https://blog.thetruckercodex.com/common-dot-violations-how-to-avoid/).

## What Severity Weight Accumulation Signals to FMCSA

FMCSA's intervention model is not purely reactive. When a carrier's BASIC percentile crosses 65% for non-passenger, non-HM carriers in certain BASICs, the agency begins prioritization for warning letters. Crossing 75–80% in multiple BASICs triggers eligibility for targeted roadside enforcement campaigns. Hitting investigation thresholds — which vary by BASIC — puts the carrier in the queue for a compliance review.

The critical point: it is the **combination** of severity weight accumulation and percentile rank against peer carriers that drives these decisions. A carrier with 50 low-severity violations may score better than a carrier with 8 high-severity OOS violations, depending on peer group composition. This is why [DOT audit trigger patterns](https://blog.thetruckercodex.com/dot-compliance-audit-triggers/) are directly traceable to specific high-weight violation clusters rather than raw violation counts.

Carriers that have already received a conditional safety rating should treat severity weight analysis as urgent — the operational and regulatory implications of that rating are examined in detail in [what a conditional safety rating actually means](https://blog.thetruckercodex.com/what-a-conditional-safety-rating-actually-means-and-how-to-f/).

## Operational Takeaways

Severity weight data is actionable if used correctly. Prioritize your pre-trip and DVIR processes around the violation codes that carry weights of 7 or higher in your problem BASICs. Any OOS-eligible violation in the past six months should be treated as a three-times multiplier event for scoring purposes. DataQ challenges on miscoded violations — particularly in HOS and Unsafe Driving — can meaningfully shift BASIC percentiles when the underlying severity weight is high. And any carrier approaching intervention thresholds should be running monthly SMS pulls, not quarterly reviews.

The severity weight table is public, the methodology is documented, and the math is deterministic. There is no justification for operating without this intelligence embedded in your compliance workflow.

---
*Data sourced from FMCSA SMS Methodology Document and FMCSA public records. Verify current enforcement thresholds at fmcsa.dot.gov.*