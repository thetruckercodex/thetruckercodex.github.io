<ul>
  {% for post in site.posts %}
    {% if post.category == "fmcsa-basics" or post.category == "basics" %}
      <li><a href="{{ post.url }}">{{ post.title }}</a></li>
    {% endif %}
  {% endfor %}
</ul>
