import os
import re
import sys
import datetime
import urllib.parse
from datetime import timezone

try:
    import google_indexer
except ImportError:
    google_indexer = None

def parse_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter
    frontmatter_match = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
    if not frontmatter_match:
        print("Error: Missing frontmatter.")
        sys.exit(1)
        
    frontmatter_text = frontmatter_match.group(1)
    body_text = content[frontmatter_match.end():].strip()

    meta = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
            
    return meta, body_text

def convert_body_to_html(body_text):
    # Extremely simple markdown parser for the specific needs
    # Extract Hussein's Take if present
    take_match = re.search(r'##\s*(Hussein\'s Take|رأي حسين|HUSSEIN\'S TAKE)(.*?)(?=##|\Z)', body_text, re.IGNORECASE | re.DOTALL)
    take_text = ""
    if take_match:
        take_text = take_match.group(2).strip()
        body_text = body_text.replace(take_match.group(0), "")

    html_parts = []
    
    # Simple markdown replacements
    for p in body_text.split('\n\n'):
        p = p.strip()
        if not p: continue
        
        if p.startswith('## '):
            html_parts.append(f"<h2>{p[3:].strip()}</h2>")
        elif p.startswith('### '):
            html_parts.append(f"<h3>{p[4:].strip()}</h3>")
        elif p.startswith('- '):
            lines = p.split('\n')
            html_parts.append("<ul>")
            for l in lines:
                html_parts.append(f"<li>{l[2:].strip()}</li>")
            html_parts.append("</ul>")
        elif p.startswith('> '):
             html_parts.append(f"<blockquote>{p[2:].strip()}</blockquote>")
        else:
            # Inline links
            p = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', p)
            # Bold
            p = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', p)
            html_parts.append(f"<p>{p}</p>")
            
    return "\n".join(html_parts), take_text

def main(md_file):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, 'article-template.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    meta, body_text = parse_markdown(md_file)
    body_html, take_text = convert_body_to_html(body_text)
    
    now = datetime.datetime.now(timezone.utc)
    pub_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    pub_human = now.strftime('%b %d, %Y')
    read_time = str(max(2, len(body_text.split()) // 200))
    
    image_url = meta.get('image', '')
    image_url_abs = "https://ai-profit-hub.com" + image_url.replace('..', '')

    html = html.replace('ARTICLE_TITLE', meta.get('title', ''))
    html = html.replace('ARTICLE_DESCRIPTION', meta.get('description', ''))
    html = html.replace('ARTICLE_URL_SLUG', meta.get('slug', ''))
    html = html.replace('ARTICLE_IMAGE_URL_ABS', image_url_abs)
    html = html.replace('ARTICLE_IMAGE_URL', image_url)
    html = html.replace('ARTICLE_TAG', meta.get('tag', '🚀 AI News'))
    html = html.replace('ARTICLE_PUBLISHED_DATE', pub_date)
    html = html.replace('ARTICLE_PUBLISHED_HUMAN', pub_human)
    html = html.replace('ARTICLE_READ_TIME', read_time)
    html = html.replace('SOURCE_NAME', meta.get('source', 'Official Source'))
    
    html = html.replace('<!-- ARTICLE_BODY -->', body_html)
    html = html.replace('<!-- ARTICLE_TAKE -->', take_text)
    
    out_path = os.path.join(base_dir, 'articles', f"{meta.get('slug', 'output')}.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Published successfully to: {out_path}")
    
    # Ping Google Indexing API
    if google_indexer:
        target_url = f"https://ai-profit-hub.com/{meta.get('slug', '')}"
        print(f"Attempting to ping Google Indexing API for: {target_url}")
        google_indexer.ping_google(target_url)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python auto_publisher.py <file.md>")
        sys.exit(1)
    main(sys.argv[1])
