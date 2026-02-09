---
layout: page
title: FMCSA & DOT Basics
permalink: /topics/basics/
---

FMCSA and DOT compliance form the foundation of trucking regulation in the United States. These guides explain core federal requirements, regulatory structure, and recent enforcement updates affecting commercial drivers.

---

### Articles in This Topic

{% assign posts = site.posts | where: "category", "basics" %}
{% for post in posts %}
- [{{ post.title }}]({{ post.url }})
{% endfor %}
