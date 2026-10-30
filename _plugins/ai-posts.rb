# frozen_string_literal: true

require "json"
require "fileutils"
require "time"

# Agent-readable copies of the site, written after every build:
#   <page url>index.html.md  Markdown copy of each post and of the home page
#   /llms.txt                site map for LLMs (https://llmstxt.org)
#   /llms-full.txt           every post concatenated
#   /blog.json               structured post index
module AiPosts
  module_function

  FRONT_MATTER = /\A---\s*\r?\n.*?\r?\n---\s*\r?\n/m
  FENCE = /\A\s*(```|~~~)/
  ROOT_LINK = %r{(\]\(|(?:src|href)=["']|\A\s*\[[^\]]+\]:\s*)/(?!/)}
  CJK = /[\p{Han}\p{Hiragana}\p{Katakana}\p{Hangul}]/
  SOCIALS = {
    "github_username" => ["GitHub", "https://github.com/%s"],
    "scholar_userid" => ["Google Scholar", "https://scholar.google.com/citations?user=%s"],
    "orcid_id" => ["ORCID", "https://orcid.org/%s"],
    "linkedin_username" => ["LinkedIn", "https://www.linkedin.com/in/%s"]
  }.freeze

  def origin(site)
    site.config["url"].to_s.chomp("/")
  end

  def abs_url(site, path)
    base = site.config["baseurl"].to_s
    base = "" if base == "/"
    path = path.start_with?("/") ? path : "/#{path}"
    "#{origin(site)}#{base}#{path}"
  end

  # llms.txt convention: append .md to the page URL, or index.html.md when it is a directory.
  def markdown_path(url)
    url.end_with?("/") ? "#{url}index.html.md" : "#{url}.md"
  end

  def author_name(site)
    [site.config["first_name"], site.config["middle_name"], site.config["last_name"]]
      .map(&:to_s).reject(&:empty?).join(" ")
  end

  def summary(site)
    (site.config["llms_summary"] || site.config["description"]).to_s.strip
  end

  def iso_date(value)
    value = value.last_modified_at_time if value.respond_to?(:last_modified_at_time)
    return if value.nil?
    return value.strftime("%Y-%m-%d") if value.respond_to?(:strftime)

    Time.parse(value.to_s).strftime("%Y-%m-%d")
  rescue ArgumentError
    value.to_s
  end

  def word_count(text)
    text.scan(CJK).size + text.gsub(CJK, " ").split.size
  end

  # Source Markdown with Liquid rendered exactly as the HTML build does, so {% post_url %} resolves.
  def render_body(site, doc, payload)
    body = File.read(site.in_source_dir(doc.relative_path)).sub(FRONT_MATTER, "").strip
    if body.include?("{%") || body.include?("{{")
      payload["page"] = doc.to_liquid
      body = Liquid::Template.parse(body).render!(payload, registers: { site: site, page: payload["page"] })
    end
    absolutize_links(site, body)
  end

  # Root-relative links only work on the site itself; agents read these files out of context.
  def absolutize_links(site, markdown)
    host = origin(site)
    fenced = false
    markdown.lines.map do |line|
      if line.match?(FENCE)
        fenced = !fenced
        next line
      end
      next line if fenced

      line.gsub(ROOT_LINK) { "#{Regexp.last_match(1)}#{host}/" }
    end.join
  end

  def inline_markdown(html)
    html.to_s.gsub(%r{<a\s[^>]*href=["']([^"']+)["'][^>]*>(.*?)</a>}m, '[\2](\1)').gsub(/<[^>]+>/, "").strip
  end

  def social_links(site)
    data = site.data["socials"] || {}
    SOCIALS.filter_map do |key, (label, pattern)|
      value = data[key].to_s.strip
      [label, format(pattern, value)] unless value.empty?
    end
  end

  def post_entry(site, post, payload)
    body = render_body(site, post, payload)
    date = iso_date(post.date)
    updated = iso_date(post.data["last_modified_at"] || post.data["last_updated"])
    {
      "title" => post.data["title"].to_s,
      "date" => date,
      "updated" => updated && updated > date ? updated : nil,
      "description" => post.data["description"].to_s.strip,
      "tags" => Array(post.data["tags"]).map(&:to_s).reject(&:empty?),
      "words" => word_count(body),
      "html" => abs_url(site, post.url),
      "markdown" => abs_url(site, markdown_path(post.url)),
      "path" => markdown_path(post.url),
      "body" => body
    }
  end

  def post_document(site, entry)
    lines = ["# #{entry['title']}", ""]
    lines << "- Author: #{author_name(site)}"
    lines << "- Canonical: #{entry['html']}"
    lines << "- Markdown: #{entry['markdown']}"
    lines << "- Date: #{entry['date']}"
    lines << "- Updated: #{entry['updated']}" if entry["updated"]
    lines << "- Tags: #{entry['tags'].join(', ')}" unless entry["tags"].empty?
    lines << "- Description: #{entry['description']}" unless entry["description"].empty?
    lines << "" << entry["body"] << ""
    lines.join("\n")
  end

  def home_document(site, home, body, entries)
    lines = ["# #{author_name(site)}", ""]
    subtitle = inline_markdown(home.data["subtitle"])
    lines << subtitle << "" unless subtitle.empty?
    lines << "- Canonical: #{abs_url(site, home.url)}"
    lines << "- Markdown: #{abs_url(site, markdown_path(home.url))}"
    social_links(site).each { |label, url| lines << "- #{label}: #{url}" }
    lines << "- Blog map for agents: #{abs_url(site, '/llms.txt')}"
    lines << "" << body << ""
    unless entries.empty?
      lines << "## Recent posts" << ""
      entries.first(5).each { |e| lines << "- [#{e['title']}](#{e['markdown']}) (#{e['date']})" }
      lines << ""
    end
    lines.join("\n")
  end

  def llms_index(site, home_words, entries)
    last = entries.map { |e| e["updated"] || e["date"] }.max
    lines = ["# #{author_name(site)}", "", "> #{summary(site)}", ""]
    lines << "Every post and the home page also exist as Markdown: append `index.html.md` to the page URL"
    lines << "(e.g. #{entries.first['html']} -> #{entries.first['markdown']})." if entries.any?
    lines << "Prefer the Markdown copies over HTML."
    lines << "" << "Last updated: #{last}" if last
    lines << "" << "## About" << ""
    lines << "- [#{author_name(site)}](#{abs_url(site, markdown_path('/'))}): bio, research interests, and links (#{home_words} words)"
    lines << "" << "## Posts" << ""
    entries.each do |e|
      line = "- [#{e['title']}](#{e['markdown']}) (#{e['date']}, #{e['words']} words)"
      line += ": #{e['description']}" unless e["description"].empty?
      lines << line
    end
    lines << "" << "## Optional" << ""
    lines << "- [All posts in one file](#{abs_url(site, '/llms-full.txt')}): every post concatenated as Markdown (#{entries.sum { |e| e['words'] }} words)"
    lines << "- [JSON index](#{abs_url(site, '/blog.json')}): titles, dates, tags, word counts, HTML and Markdown URLs"
    lines << "- [Atom feed](#{abs_url(site, '/feed.xml')}): feed of recent posts"
    lines << "- [Blog](#{abs_url(site, '/blog/')}): HTML listing of posts"
    lines << ""
    lines.join("\n")
  end

  def write(site, path, content)
    out = site.in_dest_dir(path)
    FileUtils.mkdir_p(File.dirname(out))
    File.write(out, content)
  end

  module Filters
    def ai_markdown_path(url)
      AiPosts.markdown_path(url.to_s)
    end
  end
end

Liquid::Template.register_filter(AiPosts::Filters)

# Rouge puts the language class on a wrapper div, but HTML-to-Markdown converters (and the
# language label in copy_code.js) only read it from <code>, so copy it there. Plain text stays unlabelled.
Jekyll::Hooks.register [:documents, :pages], :post_convert do |doc|
  next unless doc.content&.include?("highlighter-rouge")

  doc.content = doc.content.gsub(
    %r{(<div class="language-([\w+#.-]+) highlighter-rouge"><div class="highlight"><pre class="highlight">)<code>}
  ) do
    lang = Regexp.last_match(2)
    %w[plaintext text].include?(lang) ? Regexp.last_match(0) : "#{Regexp.last_match(1)}<code class=\"language-#{lang}\">"
  end
end

Jekyll::Hooks.register :site, :post_write do |site|
  payload = site.site_payload
  entries = site.posts.docs.sort_by(&:date).reverse.map { |post| AiPosts.post_entry(site, post, payload) }
  entries.each { |e| AiPosts.write(site, e["path"], AiPosts.post_document(site, e)) }

  home = site.pages.find { |page| page.url == "/" }
  home_words = 0
  if home
    body = AiPosts.render_body(site, home, payload)
    home_words = AiPosts.word_count(body)
    AiPosts.write(site, AiPosts.markdown_path(home.url), AiPosts.home_document(site, home, body, entries))
  end

  AiPosts.write(site, "llms.txt", AiPosts.llms_index(site, home_words, entries))

  full = ["# #{AiPosts.author_name(site)} — blog", "", "> #{AiPosts.summary(site)}", ""]
  entries.each { |e| full << AiPosts.post_document(site, e).rstrip << "" << "---" << "" }
  AiPosts.write(site, "llms-full.txt", full.join("\n"))

  index = {
    "name" => AiPosts.author_name(site),
    "url" => AiPosts.abs_url(site, "/"),
    "about_markdown" => AiPosts.abs_url(site, AiPosts.markdown_path("/")),
    "blog" => AiPosts.abs_url(site, "/blog/"),
    "llms" => AiPosts.abs_url(site, "/llms.txt"),
    "llms_full" => AiPosts.abs_url(site, "/llms-full.txt"),
    "feed" => AiPosts.abs_url(site, "/feed.xml"),
    "posts" => entries.map { |e| e.except("path", "body").compact }
  }
  AiPosts.write(site, "blog.json", JSON.pretty_generate(index) + "\n")
end
