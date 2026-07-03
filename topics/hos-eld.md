---
layout: category_page
title: HOS & ELD
permalink: /topics/hos-eld/
description: "Hours-of-Service and Electronic Logging Device compliance under 49 CFR Part 395: driving limits, on-duty windows, exemptions, and enforcement exposure."
---

Hours-of-Service (HOS) regulations under **49 CFR Part 395** exist to control driver fatigue, one of the most statistically significant contributors to commercial motor vehicle crashes. Since December 2017, compliance has been enforced primarily through the Electronic Logging Device (ELD) mandate (49 CFR §395.8, §395.22), which replaced paper logs with automated, tamper-resistant recording of duty status.

## Core HOS Limits

Property-carrying drivers operate under a structure of interacting limits: the 11-hour driving limit within a 14-hour on-duty window, a mandatory 30-minute break after 8 cumulative hours of driving, and either a 60-hour/7-day or 70-hour/8-day cumulative duty limit depending on carrier operating schedule. The 10-hour off-duty (or equivalent sleeper berth split) reset governs when the clock restarts.

## ELD Compliance Architecture

ELDs must be registered on FMCSA's list of certified devices, correctly configured for the carrier's operation, and supported by a driver capable of producing records on request during a roadside inspection. Malfunction and data diagnostic events must be handled under defined protocols — an unresolved malfunction does not excuse continued non-compliant recordkeeping.

## Common Enforcement Exposure

Roadside officers and auditors frequently focus on unassigned driving segments, personal conveyance misuse, form-and-manner errors in supporting documents, and log edits lacking driver certification. HOS and ELD violations feed directly into the Hours-of-Service Compliance BASIC under the Safety Measurement System (SMS), and falsification indicators can escalate a routine inspection into a broader compliance review.

## Exemptions and Edge Cases

Several regulatory exemptions modify the base HOS framework, including the short-haul exemption, adverse driving conditions exemption, and agricultural/seasonal provisions — each with narrow qualifying conditions and distinct documentation obligations that must be independently verified for every trip.

### Articles in This Topic

{% assign posts = site.posts | where: "category", "hos-eld" %}
{% for post in posts %}
- [{{ post.title }}]({{ post.url }})
{% endfor %}

<br>
[← All Topics](/topics/)
