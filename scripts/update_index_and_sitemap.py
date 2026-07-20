import os
import re

def parse_md(f):
    with open(f, encoding='utf-8') as file:
        content = file.read()
        fm = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
        meta = {}
        if fm:
            for line in fm.group(1).split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
articles = [
    parse_md(os.path.join(base_dir, '..', 'kimi-k3-moonshot-ai.md')),
    parse_md(os.path.join(base_dir, '..', 'gpt56-sol-review.md')),
    parse_md(os.path.join(base_dir, '..', 'apple-openai-lawsuit.md'))
]

index_path = os.path.join(base_dir, 'index.html')
sitemap_path = os.path.join(base_dir, 'sitemap.xml')

# Update index.html
with open(index_path, encoding='utf-8') as f:
    idx_content = f.read()

new_cards = ''
for m in articles:
    new_cards += f'''<article class="article-card animate-in">
        <img src="{m['image']}" alt="{m['title']}" class="article-card-image" loading="lazy" decoding="async" width="800" height="450">
        <div class="article-card-body">
          <span class="article-card-tag">{m.get('tag', '🚀 AI News')}</span>
          <h2 class="article-card-title"><a href="articles/{m['slug']}.html">{m['title']}</a></h2>
          <p class="article-card-excerpt">{m['description']}</p>
          <div class="article-card-meta">
            <span class="article-date">July 17, 2026</span>
          </div>
        </div>
      </article>\n'''

if 'kimi-k3-moonshot-ai-largest-open-model-2026.html' not in idx_content:
    idx_content = idx_content.replace('<div class="articles-grid">', '<div class="articles-grid">\n' + new_cards)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(idx_content)
    print('Updated index.html')
else:
    print('index.html already contains these articles')

# Update sitemap.xml
with open(sitemap_path, encoding='utf-8') as f:
    sitemap_content = f.read()

new_urls = ''
today = '2026-07-17T12:00:00Z'
for m in articles:
    new_urls += f'''  <url>
    <loc>https://ai-profit-hub.com/articles/{m['slug']}.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>\n'''

if 'kimi-k3-moonshot-ai-largest-open-model-2026.html' not in sitemap_content:
    sitemap_content = sitemap_content.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + new_urls)
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print('Updated sitemap.xml')
else:
    print('sitemap.xml already contains these articles')
