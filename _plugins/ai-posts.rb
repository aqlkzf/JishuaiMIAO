Jekyll::Hooks.register :posts, :post_write do |post|
  # Match the slug computed in _layouts/post.liquid:
  #   page.path | remove_first: '_posts/' | remove: '.md'
  # so nested posts (e.g. _posts/notes/foo.md) resolve correctly.
  rel = post.path.sub(%r{\A.*?_posts/}, "")
  slug = rel.gsub(".md", "")

  out_path = File.join(post.site.dest, "assets", "ai-posts", "#{slug}.md.txt")
  FileUtils.mkdir_p(File.dirname(out_path))

  # At post_write, post.content has already been converted to HTML.
  # Read the source file instead so "Copy for AI" gets clean Markdown.
  markdown = File.read(post.path)
  markdown = markdown.sub(/\A---\s*\r?\n.*?\r?\n---\s*\r?\n/m, "")

  File.write(out_path, markdown)
end
