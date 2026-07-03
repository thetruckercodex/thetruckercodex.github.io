---
layout: category_page
title: Recordkeeping & Retention
permalink: /topics/recordkeeping/
description: "Structured compliance framework for FMCSA recordkeeping and retention obligations under 49 CFR Parts 385, 391, 395, and 396."
category: recordkeeping
---

In FMCSA enforcement logic, documentation is not administrative overhead — it is the primary evidentiary basis for compliance determination. A carrier may operate safely in practice yet still fail a compliance review due to incomplete, inconsistent, or improperly retained records.

This hub consolidates retention-related obligations across core federal regulatory domains.

## Regulatory Foundations

FMCSA recordkeeping requirements are embedded throughout multiple regulatory sections, including 49 CFR §391.51 (Driver Qualification File retention), 49 CFR §395.8 & §395.11 (Hours-of-Service records and supporting documents), 49 CFR §396.3 & §396.11 (inspection, repair, and maintenance records), 49 CFR Part 382 (drug and alcohol testing program documentation), and 49 CFR Part 385 (safety fitness evaluation procedures). Retention timelines vary by document type, and misclassification of retention duration is a common audit finding.

## Core Retention Categories

Driver Qualification Files must retain the employment application, MVRs (initial and annual), Medical Examiner's Certificate, road test certificate, and safety performance history inquiries for the duration of employment plus 3 years. Hours-of-Service records — ELD data, supporting documents, and driver certification logs — carry a minimum 6-month retention standard. Inspection, repair, and maintenance records typically require 12 months while the vehicle is in service plus 6 months after leaving control. Drug and alcohol testing documentation retention varies by result category: 5 years for positive results, 1 year for negative results.

## Audit Exposure Patterns

Three systemic failure patterns recur during compliance reviews: fragmented storage across email threads and disconnected systems, retention miscalculation (documents deleted prematurely or retained without expiration logic), and corrective action gaps where repairs are performed but no documentary trace is maintained.

## Enforcement Logic: Burden of Proof

Under FMCSA enforcement standards, the burden of demonstrating compliance rests on the carrier — absence of documentation is interpreted as absence of compliance, not a clerical error.

{% assign posts = site.posts | where: "category", "recordkeeping" %}
### Articles in This Topic
{% for post in posts %}
- [{{ post.title }}]({{ post.url }})
{% endfor %}

<br>
[← All Topics](/topics/)
