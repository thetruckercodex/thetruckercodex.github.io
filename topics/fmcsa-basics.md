<ul>
  {% for post in site.posts %}
    {% if post.categories contains "fmcsa-basics" or post.category == "fmcsa-basics" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a>
      </li>
    {% endif %}
  {% endfor %}
</ul>
