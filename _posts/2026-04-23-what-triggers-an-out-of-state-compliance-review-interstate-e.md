---
layout: post
title: "What Triggers an Out-of-State Compliance Review: Interstate Enforcement Data"
date: 2026-04-23
categories: audits-violations
description: "Enforcement intelligence analysis: What Triggers an Out-of-State Compliance Review: Interstate Enforcement Data. Data-driven insights from FMCSA and CVSA records for motor carriers and compliance professionals."
---

Interstate carriers operate under a compliance architecture that doesn't stop at state lines — and neither does enforcement. When a carrier domiciled in Texas accumulates roadside inspection violations in Georgia, Ohio, and Illinois, FMCSA's Safety Measurement System registers that pattern regardless of which state generated the data. The resulting safety scores feed a prioritization model that can trigger a compliance review conducted by investigators from a state entirely different from the carrier's home jurisdiction. Understanding what activates that mechanism is operationally critical.

## How FMCSA's SMS Feeds the Interstate Enforcement Pipeline

FMCSA's Safety Measurement System aggregates violation and crash data across all 50 states using a rolling 24-month window. Every roadside inspection, every reportable crash, and every out-of-service order enters the system and gets weighted against carrier-specific expected values derived from peer groups with similar operations. The output — BASIC percentile scores — directly determines whether a carrier surfaces for intervention.

### The Percentile Thresholds That Activate Reviews

FMCSA publishes intervention thresholds by BASIC category. When a carrier's percentile score in a given BASIC exceeds the alert threshold, that carrier becomes eligible for prioritized intervention. Current thresholds that push carriers toward compliance review include:

- **Unsafe Driving BASIC**: ≥65th percentile for non-passenger/non-HM carriers (≥50th for passenger or HM carriers)
- **Hours-of-Service Compliance BASIC**: ≥65th percentile
- **Vehicle Maintenance BASIC**: ≥80th percentile
- **Controlled Substances/Alcohol BASIC**: ≥65th percentile
- **Driver Fitness BASIC**: ≥80th percentile

A carrier breaching multiple BASIC thresholds simultaneously accelerates the timeline from SMS flag to actual investigator contact. FMCSA's intervention data consistently shows that multi-BASIC threshold exceedances are the dominant predictor of compliance review selection — a pattern analyzed in depth at [how FMCSA selects carriers for compliance reviews](https://blog.thetruckercodex.com/how-fmcsa-selects-carriers-for-compliance-reviews-the-data-b/).

## FMCSA Out-of-State Compliance Review Triggers Interstate: The Specific Data Patterns

The question isn't just what score triggers a review — it's what operational behavior generates that score across multiple states. FMCSA's [intervention framework](https://www.fmcsa.dot.gov/safety/carrier-safety/interventions) categorizes compliance reviews as either offsite or onsite, and the triggering data often originates from enforcement activity far removed from the carrier's home state.

### Roadside Inspection Accumulation Across State Lines

CVSA-certified inspections conducted under the North American Standard Inspection Program feed uniformly into SMS regardless of the inspecting state. A carrier running regular lanes through the I-95 corridor will accumulate inspection records from multiple states. When violations under 49 CFR Part 393 (vehicle maintenance) or Part 395 (hours of service) appear repeatedly across different state inspections, the severity-weighted SMS algorithm amplifies those scores faster than single-state violation clusters would.

Specific violation codes with outsized SMS weight include:

- **393.9** — Inoperative required lamps (lighting violations remain among the highest-frequency OOS triggers)
- **395.8(e)** — Failure to retain driver's record of duty status
- **391.11(b)(1)** — Driver not physically qualified
- **393.45** — Brake tubing and hose adequacy failures
- **383.23** — Operation without valid CDL (a Driver Fitness violation with immediate regulatory consequence)

For a detailed breakdown of how inspectors verify CDL validity at the roadside and the enforcement data behind Driver Fitness violations, see [how inspectors verify CDL validity at the roadside](https://blog.thetruckercodex.com/how-inspectors-verify-cdl-validity-at-the-roadside-the-datab/).

### Crash Data and the Interstate Severity Multiplier

Crashes reported under 49 CFR Part 390.5's definition — those involving fatalities, injuries, or tow-aways — carry time-weighted severity multipliers in SMS that make recent crashes disproportionately influential. A single fatal crash in another state can spike a carrier's Crash Indicator BASIC enough to trigger intervention review within the same quarter. The mechanics of how FMCSA weights fatal, injury, and tow-away crashes in SMS scoring are documented at [how FMCSA weights fatal, injury, and tow-away crashes](https://blog.thetruckercodex.com/how-fmcsa-weights-fatal-injury-and-tow-away-crashes-in-sms-s/).

The interstate dimension is particularly acute for carriers that run high-mileage irregular routes. Their crash exposure spans multiple states, and each reportable crash regardless of jurisdiction enters the carrier's SMS record identically.

## The Investigative Handoff: Which State Conducts the Review

FMCSA operates through a network of state-partnered agencies under the Motor Carrier Safety Assistance Program (MCSAP). When a carrier domiciled in one state triggers a compliance review based on multi-state violation data, the investigation may be assigned to the carrier's home state MCSAP partner or handled directly by FMCSA regional investigators, depending on resource allocation and the severity of the triggering data.

### Warning Letters, Investigations, and Escalation Paths

FMCSA's intervention escalation sequence is structured: warning letters typically precede compliance reviews, but carriers with acute BASIC exceedances or recent out-of-service orders can bypass the warning letter stage and proceed directly to an onsite investigation. Carriers that receive warning letters and fail to demonstrate corrective action within the specified response window are prioritized for compliance review scheduling.

The full trigger taxonomy — including what distinguishes a routine compliance review from an expedited investigation — is covered in the [DOT compliance audit triggers analysis](https://blog.thetruckercodex.com/dot-compliance-audit-triggers/).

## What a Compliance Review Actually Examines

Once scheduled, a compliance review conducted under FMCSA authority will examine records across all operational jurisdictions. Investigators are not limited to violations from the carrier's home state. They will request:

- Driver qualification files under 49 CFR Part 391
- Hours-of-service records and ELD data under 49 CFR Parts 395 and 396
- Drug and alcohol testing program records under 49 CFR Part 382
- Vehicle maintenance records under 49 CFR Part 396
- Financial responsibility documentation under 49 CFR Part 387

### The Unsatisfactory Rating Consequence

Carriers that receive an Unsatisfactory safety rating following a compliance review face immediate operating authority risk. The downstream effects on registration, insurance, and continued operation are severe and, in many cases, irreversible within the carrier's current USDOT number structure. The regulatory mechanics of [what happens to operating authority after an unsatisfactory rating](https://blog.thetruckercodex.com/what-happens-to-operating-authority-after-an-unsatisfactory/) represent the terminal end of a process that typically started with unaddressed violation accumulation across multiple states.

FMCSA's [data and statistics portal](https://www.fmcsa.dot.gov/safety/data-and-statistics) publishes aggregate intervention counts that confirm the scale: thousands of compliance reviews are initiated annually, with multi-state carriers representing a disproportionate share of the caseload relative to their numbers.

## Operational Takeaway

The interstate enforcement architecture means that no single state's compliance environment is safely ignorable. A carrier that manages its home-state inspection record while accumulating violations on out-of-state lanes is building exactly the multi-BASIC score pattern that FMCSA's prioritization algorithm is designed to surface. Monitor SMS scores in real time, address violation trends before they cross threshold percentiles, and treat each roadside contact in any jurisdiction as a data point in your national compliance profile.

---
*Data sourced from FMCSA Intervention Data and FMCSA public records. Verify current enforcement thresholds at fmcsa.dot.gov.*