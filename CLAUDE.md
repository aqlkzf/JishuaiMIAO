# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and Codex (openai) when working with code in this repository.

## Overview

This is a GitHub Pages personal academic website built with Jekyll using the [al-folio](https://github.com/alshedivat/al-folio) theme. The site belongs to MIAO Jishuai, a PhD student in Statistics at CUHK.

## Architecture

- `_pages/about.md` — the homepage (bio, profile photo, latest posts)
- `_pages/blog.md` — blog listing page with pagination
- `_posts/` — blog posts in `YYYY-MM-DD-title.md` format, using `layout: post`
- `_config.yml` — Jekyll site configuration (identity, theme, plugins, features)
- `_bibliography/papers.bib` — BibTeX publications (currently empty)
- `_data/socials.yml` — social media links (GitHub, Google Scholar)
- `assets/img/prof_pic.jpg` — profile photo
- `_layouts/`, `_includes/`, `_sass/`, `_plugins/` — al-folio theme files (generally don't edit)
- `.github/workflows/deploy.yml` — GitHub Actions workflow for building and deploying

## Deployment

The site is deployed via GitHub Actions. On push to `main`, the workflow builds the Jekyll site and deploys to the `gh-pages` branch. GitHub Pages serves from `gh-pages`.

URL: https://aqlkzf.github.io/

## Local Development

```bash
bundle install
bundle exec jekyll serve
```

Or with Docker:
```bash
docker compose up
```

## Adding Content

### New blog post
Create `_posts/YYYY-MM-DD-title.md` with frontmatter:
```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
description: "Brief description"
tags: tag1 tag2
---
```

### Navigation
Pages appear in the navbar if they have `nav: true` in frontmatter. Order is controlled by `nav_order`.
