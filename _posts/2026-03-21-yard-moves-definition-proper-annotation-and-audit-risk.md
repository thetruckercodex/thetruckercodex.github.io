---
layout: post
title: "Yard Moves: Definition, Proper Annotation, and Audit Risk"
date: 2026-03-21
categories: hos-eld
description: "Comprehensive analysis of Yard Moves: Definition, Proper Annotation, and Audit Risk under 49 CFR Part 395. Regulatory requirements, enforcement consequences, and compliance guidance for motor carriers."
---

The yard move provision is one of the most operationally valuable—and most frequently misapplied—exceptions available under federal hours-of-service regulations. When used correctly, it allows commercial motor vehicle drivers to record on-premises vehicle movement without accumulating on-duty driving time. When misused, it generates the kind of ELD data inconsistencies that trigger enforcement action, Compliance, Safety, Accountability (CSA) point accumulation, and potential carrier liability. This analysis examines the regulatory basis, proper ELD annotation mechanics, and the specific audit exposures carriers create when yard move procedures break down.

---

## Regulatory Foundation: What 49 CFR § 395.2 Actually Defines

The yard move is codified not as a standalone term within 49 CFR § 395.2, but as a component of the **on-duty not driving** status under the ELD technical specifications referenced in Part 395. The [full definitional framework at § 395.2](https://www.ecfr.gov/current/title-49/part-395/section-395.2) establishes "on-duty time" to include all time spent operating a CMV, with the critical exception carved out in the ELD mandate final rule: movement occurring at a **terminal, facility, or transportation hub** that meets the threshold conditions for yard move designation may be recorded as a non-driving on-duty status, provided the ELD is properly annotated.

The operative regulatory structure comes from 49 CFR § 395.26(b), which governs ELD special driving categories, and § 395.28, which addresses ELD data editing and annotation requirements. Together, these provisions establish that yard move status is a **driver-initiated special category** that the ELD must support and that requires a location-specific annotation when selected.

### The Three Threshold Conditions for Yard Move Eligibility

Not every instance of slow, on-premises vehicle movement qualifies as a yard move. FMCSA guidance and the ELD technical specifications establish three conditions that must be satisfied simultaneously:

- **The vehicle must be operated on private property or a recognized terminal/facility**—public roadways, even those immediately adjacent to a facility, categorically disqualify a movement from yard move status.
- **The movement must be authorized by the motor carrier**—ad hoc or driver-initiated repositioning without carrier authorization does not meet the regulatory threshold.
- **The driver must be operating a CMV subject to Part 395**—drivers fully exempt from ELD requirements under § 395.8(f) do not require yard move annotation, but carriers operating mixed fleets should establish uniform procedures to avoid systemic gaps.

Critically, the regulation places no maximum distance or speed threshold for yard moves. The qualifying factor is the nature and location of the movement, not its duration. However, extended yard move periods—particularly those lasting more than 30 to 45 minutes—frequently attract scrutiny during audits because they suggest either public roadway use or misclassification of line-haul driving segments.

---

## Yard Moves ELD Annotation Rules: Mechanics and Carrier Obligations

Understanding [ELD compliance](https://blog.thetruckercodex.com/electronic-logging-device-eld-compliance/) at the system level is a prerequisite for implementing yard move procedures correctly. The ELD technical specifications (Appendix to Subpart B of Part 395) require that when a driver selects the yard move special driving category, the ELD must capture the following data elements at the time of selection:

- Event type and status change timestamp
- Vehicle location coordinates (or the nearest recognizable location if GPS is unavailable)
- Driver annotation confirming the nature of the movement
- Carrier or co-driver confirmation where applicable

### Annotation Content Standards

The annotation requirement under § 395.28 is not merely a checkbox function. FMCSA inspection guidance clarifies that annotations must be **specific, contemporaneous, and location-identifiable**. An annotation that reads "yard move" without a facility name, terminal identifier, or location description does not satisfy the specificity standard. Best practice—and the standard applied by experienced DOT auditors—requires annotations to include the facility name or terminal identifier, the nature of the movement (e.g., "repositioning trailer to dock 14"), and the time the movement began and ended if the ELD does not automatically capture status change timestamps with sufficient granularity.

Carriers should also be aware that the editing and annotation provisions of § 395.28 apply retroactively: drivers and carriers may add annotations after the fact, but any post-hoc annotation creates an edit record that is visible to auditors. A pattern of retroactive yard move annotations is a documented [DOT audit trigger](https://blog.thetruckercodex.com/dot-compliance-audit-triggers/) that investigators use to identify systematic misclassification of driving time.

### Carrier Recordkeeping Obligations

Under § 395.8(k), carriers must retain ELD records—including all yard move annotations and edit histories—for a minimum of six months. Carriers operating terminals with high daily yard move volumes should implement a written yard move authorization policy that documents which facilities are approved for yard move status, which drivers are authorized to use it, and what annotation standards apply. This policy document becomes a primary reference artifact during an FMCSA investigation.

---

## Audit Risk: Where Yard Move Compliance Breaks Down

The most consequential enforcement exposure related to yard moves arises not from a single misannotated event but from **systemic patterns** visible across the carrier's ELD data set. FMCSA investigators conducting a compliance review under 49 CFR Part 385 examine ELD records for several specific anomalies:

- Yard move events recorded in locations that GPS data places on or near public roadways
- Yard move durations that correlate with travel times inconsistent with on-site repositioning
- Missing or generic annotations on yard move status changes
- A disproportionate volume of yard moves at facilities that do not appear in the carrier's operating authority or terminal documentation
- Yard move events used to interrupt what would otherwise be a continuous driving period, suggesting intentional HOS manipulation

This last pattern is particularly serious. When investigators find yard moves inserted within long driving segments in a manner that appears designed to reset the 11-hour driving limit or extend available duty time, the matter may be referred for a pattern-and-practice investigation. Violations under § 395.3(a)(3) for exceeding the 11-hour driving limit carry a maximum civil penalty of **$16,864 per violation** under current FMCSA penalty schedules, and if the misuse of yard move status is shown to be knowing and willful, penalties can escalate significantly.

This enforcement dynamic is analogous to the scrutiny applied to [personal conveyance misuse](https://blog.thetruckercodex.com/personal-conveyance-what-fmcsa-actually-permits/)—another special driving category where legitimate regulatory relief is frequently converted into a compliance liability through inconsistent or pretextual application. Carriers developing unified special-category policies should address yard moves and personal conveyance together to ensure annotation standards are internally consistent.

It is also worth noting that yard move misclassification interacts with other HOS provisions. A driver who incorrectly records a 45-minute public roadway segment as a yard move may simultaneously be masking a violation of the [short-haul exemption's 150 air-mile radius requirement](https://blog.thetruckercodex.com/short-haul-exemption-who-qualifies-and-what-records-are-requ/) or a violation of the [adverse driving conditions extension](https://blog.thetruckercodex.com/adverse-driving-conditions-exemption-when-and-how-to-apply-i/) criteria. Auditors trained in ELD analysis are specifically directed to cross-reference special-category events against GPS coordinates and timestamps to identify these compounding violations.

---

## Compliance Posture: Practical Standards for Carriers

Carriers who want to use yard moves as the legitimate operational tool they are designed to be should implement the following minimum standards:

1. **Maintain a written list of approved yard move facilities** with physical addresses and GPS boundary references, distributed to all drivers operating at those locations.
2. **Establish annotation templates** that drivers can select or populate quickly, ensuring location-specific content without relying on free-form text that varies by driver.
3. **Conduct quarterly ELD data audits** that specifically filter and review all yard move events for annotation completeness, GPS location consistency, and duration reasonableness.
4. **Train dispatchers** to recognize that assigning a driver to move a vehicle on a public road—even briefly—does not qualify for yard move status, regardless of proximity to a terminal entrance.
5. **Document the training** in the driver qualification file with a signed acknowledgment that covers yard move procedures specifically.

The [FMCSA's regulatory framework](https://www.fmcsa.dot.gov/) for ELD special driving categories was designed with the operational realities of large terminal operations in mind. Yard move status is a legitimate and necessary tool. The compliance risk is not in using it—it is in using it without the annotation discipline that makes it defensible under audit.

---

## Regulatory Reference

| Citation | Subject |
|---|---|
| 49 CFR § 395.2 | Definitions — On-Duty Time, Hours of Service |
| 49 CFR § 395.3(a)(3) | Maximum driving time — property-carrying drivers |
| 49 CFR § 395.8(k) | ELD record retention requirements |
| 49 CFR § 395.26(b) | ELD special driving categories — yard move and personal conveyance |
| 49 CFR § 395.28 | ELD data editing and annotation requirements |
| 49 CFR Part 385 | Safety fitness procedures — compliance review standards |
| Appendix to Subpart B, Part 395 | ELD technical specifications — data capture requirements |

---

*Regulatory references verified against current eCFR and FMCSA official sources. Verify applicability for your specific operation. This post does not constitute legal advice.*