# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) and Codex (openai) when working with code in this repository.

## Overview

This is a GitHub Pages personal academic website built with Jekyll using the `jekyll-theme-minimal` theme. The site belongs to MIAO Jishuai, a PhD student in Statistics at CUHK.

## Architecture

- `README.md` — the homepage content (Jekyll renders this as `index.html` on GitHub Pages)
- `_config.yml` — Jekyll site configuration (title, logo, description, theme)
- `assets/img/photo.jpg` — profile photo referenced in `_config.yml`

There are no layout files or additional pages — all content lives in `README.md`, and the `jekyll-theme-minimal` theme handles all styling.

## Local Development

```bash
# Serve the site locally (requires Ruby + bundler + jekyll)
bundle exec jekyll serve

# If no Gemfile exists, install jekyll first:
gem install jekyll bundler
jekyll new . --force   # or add a Gemfile manually
bundle exec jekyll serve
```

The site is deployed automatically by GitHub Pages on push to `main`.

## Content Updates

To update the homepage, edit `README.md`. Markdown is rendered directly by Jekyll. To change the site title, logo, or description, edit `_config.yml`.
