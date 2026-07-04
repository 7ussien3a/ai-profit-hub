#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Profit Hub - Auto Publisher v4.0 (Template-Driven Edition)
=============================================================
إعادة كتابة كاملة لحل المشاكل الجذرية:
  - Gemini يولّد المحتوى فقط (لا HTML كامل) -> لا مزيد من القوالب المهلوسة
  - الناشر يحمّل article-template.html من القرص ويملأ الـ placeholders
  - كل مقال جديد يحصل على: GA, canonical, meta dates, JSON-LD, روابط مطلقة صحيحة
  - slugify يدعم Unicode (يمنع mojibake مثل jeff-bezos8217s-)
  - بوابة جودة إجبارية قبل النشر
  - إعدادات مركزية من publish-config.json (لا hardcoded IDs)

الاستخدام:
    python auto_publisher.py              # نشر مقال واحد
    python auto_publisher.py --topic "..." # بموضوع محدد
    python auto_publisher.py --dry-run     # توليد بدون push

التوافق: Python 3.8+، يعمل بـ urllib فقط (لا مكتبات خارجية).
"""

import os
import sys
import io
import json
import re
import html
import unicodedata
import datetime
import glob
import subprocess
import urllib.request
import urllib.error

# Force UTF-8 stdout so emojis don't appear as ?? on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# 1) تحميل الإعدادات
# ============================================================
# يدعم موقعين للسكربت:
#   (أ) الجذر:    مشروع قوقل ادسنس/auto_publisher.py        → ROOT_DIR = cwd
#   (ب) داخل site: site/scripts/auto_publisher.py            → SITE_DIR = parent.parent
# الاكتشاف تلقائي حسب وجود مجلد 'site' بجوار السكربت.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(_SCRIPT_DIR, 'site')):
    # الحالة (أ): السكربت في الجذر
    ROOT_DIR = _SCRIPT_DIR
    SITE_DIR = os.path.join(_SCRIPT_DIR, 'site')
else:
    # الحالة (ب): السكربت داخل site/scripts/
    SITE_DIR = os.path.dirname(os.path.dirname(_SCRIPT_DIR))  # = site/
    ROOT_DIR = os.path.dirname(SITE_DIR)                      # = مشروع قوقل ادسنس/
ARTICLES_DIR = os.path.join(SITE_DIR, 'articles')
CONFIG_PATH = os.path.join(_SCRIPT_DIR, 'publish-config.json')
if not os.path.exists(CONFIG_PATH):
    # fallback: ابحث عن config بجوار site/
    CONFIG_PATH = os.path.join(ROOT_DIR, 'publish-config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

# تحميل GEMINI_API_KEY من .env (ابحث في ROOT_DIR ثم SITE_DIR)
ENV_PATH = os.path.join(ROOT_DIR, '.env')
if not os.path.exists(ENV_PATH):
    ENV_PATH = os.path.join(SITE_DIR, '.env')
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    print("[FATAL] GEMINI_API_KEY is not set. Create .env with: GEMINI_API_KEY=...")
    sys.exit(1)


# ============================================================
# 2) أدوات مساعدة
# ============================================================
def slugify(text):
    """slugify يدعم Unicode + HTML entities. يمنع 'jeff-bezos8217s-'."""
    text = html.unescape(text)                                   # &#8217; -> '
    text = unicodedata.normalize('NFKD', text)                   # تفكيك التشكيل
    text = text.encode('ascii', 'ignore').decode('ascii')        # إسقاط non-ascii
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)                      # كل ما ليس رقماً/حرفاً -> -
    return text.strip('-')


def call_gemini(prompt, max_tokens=8192):
    """استدعاء Gemini API للحصول على نص خام (مع إعادة المحاولة)."""
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-2.5-flash:generateContent?key=" + API_KEY)
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": max_tokens},
    }
    last_err = None
    for attempt in range(3):
        req = urllib.request.Request(
            url, data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}, method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            if e.code in (503, 429, 500) and attempt < 2:
                wait = (attempt + 1) * 15
                print(f"  HTTP {e.code} - retry in {wait}s...")
                import time; time.sleep(wait); continue
            print(f"[ERROR] Gemini API {e.code}: {body[:300]}")
            sys.exit(1)
        except Exception as e:
            last_err = e
            if attempt < 2:
                import time; time.sleep(5); continue
            print(f"[ERROR] Gemini failed: {e}")
            sys.exit(1)


def get_existing_articles():
    """قائمة بالمقالات الموجودة لتفادي التكرار."""
    existing = []
    for path in glob.glob(os.path.join(ARTICLES_DIR, "*.html")):
        name = os.path.basename(path)
        slug = re.sub(r'-\d{8}(?:-\d{6})?\.html$', '', name)
        existing.append(slug.replace('-', ' '))
    return existing


def detect_category(title):
    """كشف التصنيف المناسب من العنوان."""
    t = title.lower()
    cats = CONFIG['categories']
    rules = [
        ('coding', ['code', 'programming', 'developer', 'copilot', 'cursor', 'xcode', 'github']),
        ('video', ['video', 'youtube', 'veo', 'sora', 'kling', 'avataar']),
        ('writing', ['writing', 'blog', 'content', 'copy']),
        ('business', ['business', 'startup', 'funding', 'revenue', 'layoff', 'enterprise']),
        ('ethics', ['ethics', 'law', 'regulation', 'privacy', 'ban', 'lawsuit']),
        ('productivity', ['productivity', 'automation', 'workflow', 'notion']),
        ('tools', ['tool', 'review', 'best', 'free', 'alternative', 'directory']),
    ]
    for cat_key, keywords in rules:
        if any(kw in t for kw in keywords):
            return cats[cat_key]
    return cats['news']


def estimate_read_time(text):
    """تقدير وقت القراءة (~200 كلمة/دقيقة)."""
    words = len(re.findall(r'\b\w+\b', text))
    return max(5, round(words / 200))


# ============================================================
# 3) توليد المحتوى عبر Gemini
# ============================================================
def generate_topic(existing):
    """توليد عنوان فريد."""
    recent = "\n".join(existing[-20:])
    prompt = (
        "You are an expert tech blog editor. Give me ONLY ONE highly engaging, "
        "trending, click-worthy title for an article about AI Tools, Startups, "
        "or Technology. Do NOT use quotes or extra text. Just the title.\n\n"
        "It MUST NOT be similar to these already published:\n" + recent
    )
    title = call_gemini(prompt, max_tokens=100).strip().strip('"*').strip()
    title = html.unescape(title)
    return title


def generate_content(title):
    """توليد محتوى المقال فقط (بدون HTML كامل)."""
    cat = detect_category(title)
    prompt = f"""You are an expert SEO content writer. Write an in-depth article titled "{title}".

CRITICAL RULES:
1. OUTPUT: Plain Markdown only (NOT HTML). Use ## for H2, ### for H3.
2. LENGTH: Minimum 900 words. Be detailed, thorough, actionable.
3. STRUCTURE: Introduction, 4-6 main sections with ##, conclusion, 3 FAQ questions.
4. TONE: Authoritative, engaging, fact-based.
5. NO fabricated quotes, NO made-up statistics without clear hedging.
6. Category: {cat['emoji']} {cat['name']}

OUTPUT FORMAT (strict):
LINE 1: A compelling 150-character meta description (no quotes).
LINE 2: blank
LINE 3+: The full article body in Markdown.

Start with the description on line 1, immediately."""
    raw = call_gemini(prompt, max_tokens=8192).strip()
    if raw.startswith('```'):
        raw = re.sub(r'^```(?:markdown)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
    parts = raw.split('\n', 2)
    description = parts[0].strip().strip('"') if parts else ""
    body_md = parts[2].strip() if len(parts) > 2 else raw
    return description, body_md


def md_to_html(md):
    """تحويل Markdown مبسّط إلى HTML (بدون مكتبات خارجية)."""
    lines = md.split('\n')
    html_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue
        if stripped.startswith('### '):
            if in_list:
                html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
        elif stripped.startswith('## '):
            if in_list:
                html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h2 id="{slugify(stripped[3:])}">{stripped[3:]}</h2>')
        elif stripped.startswith('# '):
            continue
        elif re.match(r'^[-*]\s+', stripped):
            if not in_list:
                html_lines.append('<ul>'); in_list = True
            html_lines.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<p>{stripped}</p>')
    if in_list:
        html_lines.append('</ul>')
    return '\n'.join(html_lines)


# ============================================================
# 4) بناء المقال من القالب (Template-Driven)
# ============================================================
def download_and_optimize_image(url, slug):
    """تحميل الصورة من pollinations.ai وحفظها محلياً بصيغة jpg مباشرة بدون مكتبات خارجية."""
    final_filename = f"{slug}.jpg"
    final_path = os.path.join(SITE_DIR, 'images', final_filename)
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    
    try:
        print(f"[INFO] Downloading image from: {url}")
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
            with open(final_path, 'wb') as f:
                f.write(data)
            
        size_kb = os.path.getsize(final_path) / 1024
        print(f"[OK] Image saved: images/{final_filename} ({size_kb:.1f} KB)")
        return final_filename
    except Exception as e:
        print(f"[ERROR] Failed to download image: {e}")
        return None


def build_article(title, description, body_html, image_url_rel, image_url_abs):
    """تحميل article-template.html وتعبئة الـ placeholders."""
    template_path = os.path.join(SITE_DIR, 'article-template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        tmpl = f.read()

    slug = slugify(title)
    date_iso = datetime.date.today().isoformat()
    date_human = datetime.date.today().strftime('%B %d, %Y')
    cat = detect_category(title)
    read_time = estimate_read_time(body_html)

    replacements = {
        'ARTICLE_TITLE': title,
        'ARTICLE_DESCRIPTION': description,
        'ARTICLE_URL_SLUG': slug,
        'ARTICLE_IMAGE_URL': image_url_rel,
        'ARTICLE_IMAGE_URL_ABS': image_url_abs,
        'ARTICLE_TAG': f'{cat["emoji"]} {cat["name"]}',
        'ARTICLE_PUBLISHED_DATE': date_iso,
        'ARTICLE_PUBLISHED_HUMAN': date_human,
        'ARTICLE_READ_TIME': str(read_time),
        'SOURCE_NAME': 'AI Profit Hub Research',
        'ARTICLE_BODY': body_html,
        'ARTICLE_TAKE': f'{title} represents a significant development worth monitoring closely.',
    }
    for key, val in replacements.items():
        tmpl = tmpl.replace(key, val)
    return tmpl, slug, cat


def get_image_url(title):
    """توليد رابط صورة Pollinations."""
    keywords = re.sub(r'[^a-zA-Z0-9 ]', '', title.lower())[:60].replace(' ', '%20')
    seed = abs(hash(title)) % 10000
    return f"https://image.pollinations.ai/prompt/{keywords}?width=1600&height=900&nologo=true&seed={seed}"


# ============================================================
# 5) تحديث ملفات الموقع (index, sitemap, rss)
# ============================================================
def update_index_page(title, slug, filename, description, image_url, cat):
    """إضافة بطاقة المقال لـ index.html."""
    index_path = os.path.join(SITE_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    date_str = datetime.date.today().strftime("%B %d, %Y")
    card = f"""
      <article class="article-card animate-in">
        <img src="{image_url}" alt="{title}" class="article-card-image" loading="lazy" decoding="async" width="800" height="450">
        <div class="article-card-body">
          <span class="article-card-tag">{cat['emoji']} {cat['name']}</span>
          <h2 class="article-card-title"><a href="articles/{filename}">{title}</a></h2>
          <p class="article-card-excerpt">{description[:140]}...</p>
          <div class="article-card-meta"><span>{date_str}</span></div>
        </div>
      </article>
"""
    marker = '<div class="articles-grid">'
    if marker in content:
        content = content.replace(marker, marker + "\n" + card, 1)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] index.html updated")
    else:
        print("[WARN] articles-grid marker not found in index.html")


def update_sitemap(filename):
    """إضافة الرابط للـ sitemap.xml."""
    sitemap_path = os.path.join(SITE_DIR, 'sitemap.xml')
    date_str = datetime.date.today().isoformat()
    new_url = (f'  <url>\n    <loc>https://ai-profit-hub.com/articles/{filename}</loc>\n'
               f'    <lastmod>{date_str}</lastmod>\n'
               f'    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n</urlset>')
    try:
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '</urlset>' in content and f'/articles/{filename}</loc>' not in content:
            content = content.rsplit('</urlset>', 1)[0] + new_url
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("[OK] sitemap.xml updated")
    except Exception as e:
        print(f"[WARN] sitemap update failed: {e}")


def xml_escape(text):
    """XML escape كامل (يشمل < > & \" ')."""
    text = html.unescape(text)
    return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                 .replace('"', '&quot;').replace("'", '&apos;'))


def update_rss(title, slug, filename, description):
    """إضافة عنصر للـ RSS مع XML escaping كامل."""
    rss_path = os.path.join(SITE_DIR, 'rss.xml')
    now = datetime.datetime.now()
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S +0300")
    safe_title = xml_escape(title)
    safe_desc = xml_escape(description[:200])
    new_item = f"""  <item>
    <title>{safe_title}</title>
    <link>https://ai-profit-hub.com/articles/{filename}</link>
    <description>{safe_desc}</description>
    <pubDate>{pub_date}</pubDate>
    <guid>https://ai-profit-hub.com/articles/{filename}</guid>
  </item>
"""
    try:
        with open(rss_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'<lastBuildDate>.*?</lastBuildDate>',
                         f'<lastBuildDate>{pub_date}</lastBuildDate>', content)
        for marker in ['</atom:link>', '<channel>']:
            if marker in content:
                parts = content.split(marker, 1)
                content = parts[0] + marker + "\n" + new_item + parts[1]
                break
        with open(rss_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] rss.xml updated")
    except Exception as e:
        print(f"[WARN] rss update failed: {e}")


# ============================================================
# 6) بوابة الجودة (Pre-publish validation)
# ============================================================
def validate_article(filepath):
    """فحوصات الجودة. تُرجع (passed: bool, failures: list)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    checks = {
        'ga_present': '<!-- Google tag (gtag.js)' in content or 'googletagmanager.com/gtag/js' in content,
        'canonical_present': 'rel="canonical"' in content,
        'robots_indexable': 'index, follow' in content,
        'meta_dates': 'article:published_time' in content and 'article:modified_time' in content,
        'no_external_images': ('pollinations.ai' not in content and 'images.unsplash.com' not in content),
        'min_word_count': len(re.findall(r'\b\w+\b', re.sub(r'<[^>]+>', '', content))) >= int(CONFIG['validation']['min_word_count']),
        'has_h1': '<h1>' in content,
    }
    jsonld_ok = True
    for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', content, re.DOTALL):
        block = block.strip()
        if not block:
            continue
        try:
            json.loads(block)
        except json.JSONDecodeError:
            jsonld_ok = False
            break
    checks['jsonld_valid'] = jsonld_ok

    failures = [k for k, v in checks.items() if not v]
    return (len(failures) == 0), failures


# ============================================================
# 7) Git
# ============================================================
def push_to_github(article_filename, local_image_name, dry_run=False):
    """Commit + push."""
    if dry_run:
        print("[DRY-RUN] skipping git push")
        return
    print("[INFO] Pushing to GitHub...")
    try:
        # Force add the new article and its image (since they are in git exclude)
        subprocess.run(["git", "add", "-f", f"articles/{article_filename}"], cwd=SITE_DIR, check=True, capture_output=True)
        if local_image_name:
            subprocess.run(["git", "add", "-f", f"images/{local_image_name}"], cwd=SITE_DIR, check=True, capture_output=True)
        
        # Add index, sitemap, rss
        subprocess.run(["git", "add", "index.html", "sitemap.xml", "rss.xml"], cwd=SITE_DIR, check=True, capture_output=True)
        
        msg = f"Auto-publish: {datetime.date.today().isoformat()}"
        subprocess.run(["git", "commit", "-m", msg], cwd=SITE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=SITE_DIR, check=True, capture_output=True)
        print("[OK] Pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git failed: {e}")
        if e.stderr:
            print(e.stderr.decode('utf-8', errors='replace'))


# ============================================================
# 8) Main flow
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Profit Hub Auto Publisher v4.0")
    parser.add_argument('--topic', help="Force a specific topic/title")
    parser.add_argument('--dry-run', action='store_true', help="Generate without git push")
    args = parser.parse_args()

    print("=" * 50)
    print("AI Profit Hub - Auto Publisher v4.0")
    print("=" * 50)

    existing = get_existing_articles()

    if args.topic:
        title = html.unescape(args.topic.strip().strip('"*'))
    else:
        print("[1/6] Brainstorming topic...")
        title = generate_topic(existing)
    print(f"      Title: {title}")

    slug = slugify(title)
    date_suffix = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{slug}-{date_suffix}.html"

    print("[2/6] Generating content...")
    description, body_md = generate_content(title)
    body_html = md_to_html(body_md)

    image_url = get_image_url(title)
    local_image_name = download_and_optimize_image(image_url, slug)
    if local_image_name:
        image_url_rel = f"../images/{local_image_name}"
        image_url_abs = f"https://ai-profit-hub.com/images/{local_image_name}"
        image_url_index = f"images/{local_image_name}"
    else:
        image_url_rel = image_url
        image_url_abs = image_url
        image_url_index = image_url

    print("[3/6] Building article from template...")
    article_html, slug_out, cat = build_article(title, description, body_html, image_url_rel, image_url_abs)

    article_path = os.path.join(ARTICLES_DIR, filename)
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f"[4/6] Saved: articles/{filename}")

    print("[5/6] Validating (Quality Gate)...")
    passed, failures = validate_article(article_path)
    if not passed:
        print(f"[FAIL] Quality gate FAILED: {failures}")
        print("       Article saved but NOT published. Fix issues and re-run validation.")
        sys.exit(1)
    print("       All quality checks passed.")

    print("[6/6] Updating index/sitemap/rss...")
    update_index_page(title, slug, filename, description, image_url_index, cat)
    update_sitemap(filename)
    update_rss(title, slug, filename, description)

    push_to_github(filename, local_image_name, dry_run=args.dry_run)
    print(f"\n[DONE] Published: {title}")
    print(f"       URL: https://ai-profit-hub.com/articles/{filename}")


if __name__ == "__main__":
    main()
