---
layout: post
title: "The Compliance, Safety, Accountability Program's Public vs Non-Public Data: What Carriers Can and Can't See"
date: 2026-07-30
categories: audits-violations
description: "Enforcement intelligence analysis: The Compliance, Safety, Accountability Program's Public vs Non-Public Data: What Carriers Can and Can't See. Data-driven insights from FMCSA and CVSA records for motor carriers and compliance professionals."
---

The Compliance, Safety, Accountability (CSA) program generates considerably more data than the average carrier ever sees. FMCSA's Safety Measurement System (SMS) divides its outputs into two tiers: publicly accessible information visible to shippers, brokers, and insurers, and a restricted layer visible only to the carrier itself and enforcement personnel. Understanding exactly where that boundary falls — and what each tier contains — is not an academic exercise. Misreading it can cost you freight contracts, trigger investigations, or leave you blind to enforcement risk that is already on record.

---

## What the Public Can Actually See

The public-facing interface at [FMCSA's SMS public portal](https://ai.fmcsa.dot.gov/SMS/) displays a filtered version of carrier safety data. Any party with your USDOT number can access the following without your authorization:

- **BASIC percentile rankings** for Unsafe Driving, Hours-of-Service Compliance, Driver Fitness, Controlled Substances/Alcohol, Vehicle Maintenance, Hazardous Materials Compliance, and Crash Indicator — but *only* for carriers that meet the minimum data threshold of at least three inspections in a BASIC category over the 24-month measurement window
- **Alert flags** indicating when a carrier has exceeded intervention thresholds (formerly displayed as colored flags, now shown as threshold breach indicators)
- **Crash data**, including the number of crashes, fatalities, and injuries recorded in the MCMIS database
- **Inspection and violation counts** at the aggregate level
- **Out-of-service rates** calculated against national averages
- **Safety rating**, if one has been formally assigned following a compliance review or investigation

What the public cannot see is the underlying violation-level detail driving those percentile scores. A shipper reviewing your profile sees that your Vehicle Maintenance BASIC is in the 75th percentile. They do not see the specific inspection reports, the CFR citation codes, or the roadside weight assigned to each violation.

### The Practical Consequence for Carrier Contracting

Brokers and freight networks increasingly run automated USDOT scrapes against the public SMS data before tendering loads. A threshold breach in Unsafe Driving or Hours-of-Service Compliance — even one driven by a small number of high-severity violations — can trigger automatic disqualification in a broker's TMS before a human ever reviews the underlying facts. This is why understanding [violation severity weights and how specific citations cost more in the CSA scoring model](https://blog.thetruckercodex.com/violation-severity-weights-why-some-tickets-cost-you-more-cs/) is operationally critical, not just a compliance formality.

---

## CSA Program Public Non-Public Data Carrier Access: The Restricted Layer

The non-public tier of SMS data is accessible only through the FMCSA Portal, requiring carrier-specific PIN authentication tied to your USDOT number. This is where the enforcement-grade detail lives.

### What Only You (and FMCSA) Can See

Authenticated carrier access unlocks the following data elements that are withheld from public view:

- **Individual inspection reports** linked to specific dates, locations, and inspecting officers, including every CFR violation cited (e.g., 392.2 for general driving violations, 395.8 for hours-of-service log violations, 396.3 for inspection/repair/maintenance violations)
- **Driver-level data**, including which driver generated which roadside inspection result — a dataset that becomes particularly complex for fleets experiencing high turnover, since violations from former drivers remain attached to the carrier's record for the full 24-month window (see the compliance risk implications of this in our analysis of [driver turnover and its effect on fleet CSA exposure](https://blog.thetruckercodex.com/driver-turnover-and-compliance-risk-why-high-turnover-fleets/))
- **Acute and critical violation flags** from compliance reviews, which are not surfaced in the public percentile display but directly factor into investigation prioritization
- **Crash Preventability Determination Program (CPDP) outcomes**, where applicable — carriers who have successfully challenged crash assignments through the CPDP have those findings reflected in their non-public record before any potential public-score adjustment takes effect (for strategy on using CPDP, see [how the crash preventability program can restructure your crash record](https://blog.thetruckercodex.com/how-fmcsas-crash-preventability-determination-program-can-re/))
- **DataQs challenge history**, including the status of pending and resolved inspection record challenges

### Percentile Score Mechanics Carriers Must Understand

The authenticated view also provides the full BASIC score calculation breakdown — something carriers frequently underutilize. Each violation carries a time-weight multiplier (1x for months 13–24, 2x for months 1–12) and a severity weight ranging from 1 to 10. Violations generating an out-of-service order receive an additional severity bump. The percentile itself is calculated against a peer group segmented by carrier size and inspection exposure, not the full national carrier population. This peer-grouping dynamic has direct implications for how threshold proximity should be interpreted — a carrier at the 74th percentile in a thin peer group faces materially different enforcement risk than the same score in a densely populated peer bucket. This segmentation is analyzed in detail in our breakdown of [how BASIC percentile thresholds differ by vehicle type and carrier segment](https://blog.thetruckercodex.com/how-csas-basic-percentile-thresholds-differ-by-vehicle-type/).

---

## What Neither the Public Nor Carriers Can Directly Access

There is a third tier that sits outside both views: the full investigative file maintained by FMCSA field offices and state enforcement partners. This includes:

- **Safety investigator notes and narratives** from compliance reviews and new entrant audits
- **Prioritization scores** used internally by FMCSA to rank carriers for investigation — distinct from the public percentile display
- **Enforcement action history** below the threshold of a formal safety rating change

Carriers can request limited access to their own enforcement records through FOIA, but the standard SMS portal does not expose these records.

---

## Operational Steps for Authenticated Data Review

Carriers who authenticate into the SMS portal but fail to act on the non-public data are leaving their primary compliance intelligence tool idle. The minimum operational protocol should include:

- **Monthly review** of all new inspection entries during the active weighting window (months 1–12)
- **Immediate DataQs challenge filing** for any inspection with factual errors — the 24-month clock does not pause, and delayed challenges reduce correction value
- **Driver-level violation attribution audit** after any significant driver turnover event, mapping which records will age out and when
- **CPDP filing evaluation** for every recordable crash within 60 days of the incident, before the crash record fully propagates through MCMIS
- **Cross-referencing non-public violation detail** against your BASIC scores using the methodology outlined in our guide to [reading your CSA scorecard and identifying your highest-risk data points](https://blog.thetruckercodex.com/how-to-read-your-csa-scorecard-and-identify-your-biggest-ris/)

Comprehensive enforcement and safety statistics at the program level are maintained by FMCSA through its [data and statistics resource center](https://www.fmcsa.dot.gov/safety/data-and-statistics), which provides the national inspection volume and violation frequency data necessary for contextualizing your own percentile position.

The information asymmetry in CSA is real and structural. The public sees a score. You have access to the evidence record underlying that score. Whether you use it to defend, correct, and manage your enforcement posture — or ignore it until a compliance review forces the issue — is entirely within your operational control.

---

*Data sourced from FMCSA SMS Public Data and FMCSA public records. Verify current enforcement thresholds at fmcsa.dot.gov.*