<ul>
  {% for post in site.posts %}
    {% assign all_categories = post.categories | join: " " %}
    {% if all_categories contains "fmcsa-basics" or post.category == "fmcsa-basics" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a>
      </li>
    {% endif %}
  {% endfor %}
</ul>
