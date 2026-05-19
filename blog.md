---
layout: default
title: Blog
---

## Blog

{% for post in site.posts %}
- [{{ post.title }}]({{ post.url }}) — <small>{{ post.date | date: "%B %d, %Y" }}</small>
{% else %}
No posts yet.
{% endfor %}
