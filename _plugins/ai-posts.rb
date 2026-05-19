Jekyll::Hooks.register :posts, :post_write do |post|
  dest = File.join(post.site.dest, "assets", "ai-posts")
  FileUtils.mkdir_p(dest)
  slug = File.basename(post.path, ".*")
  File.write(File.join(dest, "#{slug}.md.txt"), post.content)
end
