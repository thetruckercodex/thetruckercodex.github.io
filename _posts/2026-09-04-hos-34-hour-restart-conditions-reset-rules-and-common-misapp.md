---
layout: post
title: "HOS 34-Hour Restart: Conditions, Reset Rules, and Common Misapplications"
date: 2026-09-04
categories: hos-eld
description: "Comprehensive analysis of HOS 34-Hour Restart: Conditions, Reset Rules, and Common Misapplications under 49 CFR Part 395. Regulatory requirements, enforcement consequences, and compliance guidance for motor carriers."
---

The 34-hour restart provision is one of the most operationally significant — and most frequently misapplied — mechanisms within the federal hours-of-service framework. Governed by [49 CFR §395.3](https://www.ecfr.gov/current/title-49/part-395/section-395.3), the restart allows a property-carrying commercial motor vehicle driver to reset the 60-hour/7-day or 70-hour/8-day cumulative on-duty limit by taking an uninterrupted off-duty period of at least 34 consecutive hours. When properly executed, it provides a critical operational reset valve. When misunderstood, it generates HOS violations that trigger out-of-service orders, civil penalties, and carrier safety rating impacts.

This analysis examines the statutory conditions for a valid restart, the mechanics of what actually resets, and the misapplications that generate the most enforcement findings in roadside inspections and compliance reviews.

---

## The Regulatory Framework for the 34 Hour Restart Rule Hours of Service

Section 395.3 establishes the maximum driving and on-duty time limits for property-carrying drivers operating under the standard HOS rules. The 34-hour restart appears at §395.3(c), which provides that a driver may restart a calculation of the 60- or 70-hour limit after the driver has had at least 34 consecutive hours in the off-duty or sleeper-berth status — or any combination thereof.

This provision interacts directly with the 60/70-hour weekly limits detailed in §395.3(b). Understanding the [60/70-hour rule and how available hours are calculated](https://blog.thetruckercodex.com/the-6070-hour-rule-how-to-calculate-your-available-hours/) is a prerequisite to correctly applying the restart, because the restart only resets the weekly cumulative — it does not extend the 11-hour driving limit or the 14-hour on-duty window for any given driving day.

### What the Restart Resets — and What It Does Not

This distinction is the source of the most consequential misapplication in practice. A valid 34-hour restart resets the driver's 60-hour or 70-hour cumulative on-duty clock to zero. It does not reset:

- The 11-hour maximum driving limit per §395.3(a)(3)
- The 14-hour on-duty window per §395.3(a)(2)
- The 30-minute break requirement under §395.3(a)(3)(ii)
- The sleeper-berth split-duty requirements under §395.1(g), if applicable
- Any adverse conditions extension already consumed

Drivers who return to duty following a 34-hour restart period with the assumption that all daily limits are freshly restored operate under a fundamental compliance error. The 14-hour clock begins running the moment the driver comes back on duty — irrespective of when the restart period concluded.

### Current Conditions: The 2020 Final Rule Baseline

FMCSA's September 2020 final rule significantly simplified the restart conditions that had been layered onto §395.3 through earlier rulemakings. The 2013 rule had imposed two restrictions that are no longer in effect: a requirement that the 34-hour period include two periods from 1:00 a.m. to 5:00 a.m. local time, and a limit of one restart use per week. Both conditions were suspended in 2014, permanently removed in 2020, and do not apply to current operations.

Under the current regulatory baseline, the sole statutory condition for a valid 34-hour restart is an uninterrupted 34-consecutive-hour period in off-duty or sleeper-berth status. No time-of-day restriction applies. No weekly frequency cap applies. A carrier operating under the 70-hour/8-day rule can, in theory, use multiple restarts within a single calendar week if operational patterns require it.

---

## Common Misapplications That Generate Enforcement Findings

### Interrupting the Restart Period

The most operationally destructive misapplication is interrupting a restart period before the 34-hour threshold is reached. Any on-duty status entry — including yard moves, pre-trip inspections logged as on-duty not driving, or brief loading activities — voids the restart accumulation. The driver must begin the 34-hour count from zero at the point of the new off-duty period.

This error is particularly acute for team drivers, drop-and-hook operations, and drivers at shipper or receiver facilities where they may be required to check in or provide documentation. ELD systems will capture the status change precisely, and an enforcement officer reviewing logs can identify a voided restart immediately. For a deeper examination of how ELD systems record and timestamp status entries, see [ELD technical specifications and what makes a device compliant](https://blog.thetruckercodex.com/eld-technical-specifications-what-makes-a-device-compliant/).

### Applying the Restart Without Exhausting Weekly Hours

The restart is not a scheduling preference — it is a mechanism to restore cumulative hours that have been consumed. Nothing in §395.3(c) prohibits a driver from taking a 34-hour off-duty period without resetting the weekly clock. However, if a driver records a 34-hour off-duty block and their ELD or logging system automatically applies a restart calculation when hours were not actually exhausted, the resulting log entries can create downstream audit discrepancies.

Carriers should ensure their back-office HOS software does not automatically trigger a restart recalculation absent explicit driver election, particularly where operations may overlap with [agricultural exemptions or other partial HOS exclusions](https://blog.thetruckercodex.com/agricultural-exemptions-which-operations-are-exempt-from-hos/) that alter the base calculation.

### Misapplying the Restart to Passenger-Carrying Operations

The 34-hour restart provision at §395.3(c) applies specifically to property-carrying drivers. Passenger-carrying CMV operations are governed by a separate regulatory framework under §395.5, which carries different daily driving limits and does not contain an equivalent restart provision in the same form. Carriers managing mixed fleets must be precise about which rule set applies to each driver. The distinctions between property and [passenger-carrying HOS rules](https://blog.thetruckercodex.com/driving-time-limits-for-passenger-carrying-cmvs-hos-differen/) represent a distinct compliance obligation.

### Enforcement Consequences

An HOS violation stemming from an invalidly claimed restart — where a driver returned to duty before accumulating 34 consecutive off-duty hours and then exceeded the 60- or 70-hour limit — is classified as an hours-of-service violation under 49 CFR Part 395. Depending on severity and pattern, consequences include:

- Driver out-of-service order under the North American Standard OOS Criteria, Article 3
- Civil penalties ranging from $1,628 to $16,284 per violation for carriers under 49 CFR §386.81 and §386 Appendix B
- Assignment of Acute or Critical HOS violations impacting the carrier's SMS BASIC score
- Potential downgrade of safety rating during a compliance review if a pattern of violations is established
- Driver disqualification exposure for egregious or repeated violations under §383.51

Carriers are strongly advised to conduct periodic internal HOS audits using the full framework outlined in the [hours-of-service rules overview](https://blog.thetruckercodex.com/hours-of-service-rules/) and to cross-reference log data against ELD records for restart integrity.

---

## Operational Compliance Checklist for Valid Restart Execution

Before a driver elects to use the 34-hour restart to reset weekly cumulative hours, the following conditions should be confirmed:

- **34 consecutive hours confirmed:** The off-duty or sleeper-berth period must reach the 34-hour threshold without any on-duty status interruption.
- **No time-of-day condition applies:** Neither 1:00–5:00 a.m. restriction nor once-per-week limitation is in effect under current §395.3(c).
- **Weekly rule set identified:** The driver is operating under either the 60/7 or 70/8 schedule — these are mutually exclusive within a single week and cannot be alternated mid-period without carrier policy and recordkeeping alignment.
- **Daily limits remain independent:** Confirm that the 11-hour driving and 14-hour on-duty windows are fresh from the moment the driver resumes duty — not from the restart start time.
- **ELD accurately captures status:** Verify that the ELD reflects the full uninterrupted off-duty block and that no automated annotations have incorrectly truncated or modified the restart period.

For regulatory source text and the full current language of §395.3, consult the [FMCSA official portal](https://www.fmcsa.dot.gov/) and the authoritative eCFR entry at [49 CFR §395.3](https://www.ecfr.gov/current/title-49/part-395/section-395.3).

---

## Regulatory Reference

| Provision | Citation | Subject |
|---|---|---|
| Maximum driving time — property | 49 CFR §395.3(a)(3) | 11-hour daily driving limit |
| On-duty window | 49 CFR §395.3(a)(2) | 14-hour on-duty limitation |
| Weekly cumulative limit | 49 CFR §395.3(b) | 60/7 and 70/8 hour limits |
| 34-hour restart | 49 CFR §395.3(c) | Restart conditions and reset mechanism |
| Passenger-carrying HOS | 49 CFR §395.5 | Separate daily and weekly limits |
| Civil penalties | 49 CFR Part 386, Appendix B | Penalty schedule for HOS violations |

---

*Regulatory references verified against current eCFR and FMCSA official sources. Verify applicability for your specific operation. This post does not constitute legal advice.*