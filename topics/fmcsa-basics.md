---
layout: category_page
title: "FMCSA & DOT Basics"
permalink: /topics/fmcsa-basics/
description: "Foundational structure of FMCSA and DOT regulatory authority over interstate motor carriers: what FMCSA is, how it regulates, and how compliance obligations attach."
---

The Federal Motor Carrier Safety Administration (FMCSA) is the agency within the U.S. Department of Transportation responsible for regulating interstate commercial motor vehicle operations, established under the Motor Carrier Safety Improvement Act of 1999. FMCSA's authority spans driver qualification, hours-of-service, vehicle maintenance, hazardous materials transport, and carrier safety fitness determination.

## How Regulatory Obligations Attach

Any entity operating commercial motor vehicles in interstate commerce above defined weight, passenger, or hazardous-materials thresholds becomes subject to FMCSA jurisdiction upon registration (typically via a USDOT number and, where applicable, operating authority/MC number). This registration event triggers ongoing obligations across recordkeeping, driver qualification, drug and alcohol testing, and vehicle maintenance — regardless of fleet size.

## The Regulatory Structure

FMCSA's core requirements are organized under Title 49 of the Code of Federal Regulations: Part 382 (Drug and Alcohol Testing), Part 383 (Commercial Driver's License standards), Part 385 (Safety Fitness Procedures), Part 386 (Rules of Practice for enforcement proceedings), Part 391 (Driver Qualification), Part 392 (Driving of Commercial Motor Vehicles), Part 395 (Hours of Service), and Part 396 (Inspection, Repair, and Maintenance).

## Safety Fitness and Risk Scoring

FMCSA administers the Safety Measurement System (SMS), which aggregates roadside inspection and crash data into percentile scores across seven BASIC (Behavior Analysis and Safety Improvement Category) areas. These scores inform intervention decisions — from warning letters through New Entrant Safety Audits, Compliance Reviews, and, in the most serious cases, Imminent Hazard Out-of-Service Orders that suspend a carrier's operating authority.

## New Entrant Status

Newly registered carriers operate under New Entrant status for an 18-month monitoring period, during which a New Entrant Safety Audit evaluates baseline compliance across Driver Qualification Files, HOS records, Clearinghouse status, and maintenance documentation — failure can result in registration revocation rather than a graduated penalty.

### Articles in This Topic

<ul>
  {% for post in site.posts %}
    {% capture post_data %}{{ post.category }} {{ post.categories | join: ' ' }}{% endcapture %}
    {% if post_data contains "fmcsa-basics" %}
      <li><a href="{{ post.url }}">{{ post.title }}</a></li>
    {% endif %}
  {% endfor %}
</ul>

<br>
[← All Topics](/topics/)
