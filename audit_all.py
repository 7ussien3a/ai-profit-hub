import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
FILES = sorted(ARTICLES.glob("*.html"))

report = []

for path in FILES:
    filename = path.name
    html = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r'<meta\s+http-equiv=["\']refresh["\']', html, re.IGNORECASE):
        continue

    issues = []

    text = re.sub(r"<[^>]+>", " ", html)
    words = len(text.split())
    if words < 900:
        issues.append(f"Word count is {words} (< 900)")

    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    title = title_match.group(1) if title_match else ""
    if len(title) > 60:
        issues.append(f"Meta Title length is {len(title)} (> 60)")

    desc_match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if desc_match:
        desc_len = len(desc_match.group(1))
        if desc_len < 150 or desc_len > 160:
            issues.append(f"Meta Desc length is {desc_len} (not 150-160)")
    else:
        issues.append("Missing Meta Description")

    h2_count = len(re.findall(r"<h2[^>]*>", html, re.IGNORECASE))
    if h2_count < 4 or h2_count > 6:
        issues.append(f"H2 count is {h2_count} (should be 4-6)")

    if "Hussein's Take" not in html and "Hussein" not in html:
        issues.append("Missing 'Hussein's Take' section")

    faqs = html.lower().count("faq") + html.count("?")
    if faqs < 3:
        issues.append(
            f"Possibly missing 3 FAQs (only found {faqs} question marks/FAQ keywords)"
        )

    if "Hussein Harby" not in html or "/author/hussein-harby" not in html:
        issues.append("Missing Author 'Hussein Harby' or author link")

    links = re.findall(r'<a[^>]+href=["\'](.*?)["\']', html, re.IGNORECASE)
    internal = 0
    external = 0
    for href in links:
        if href.startswith("http") and "ai-profit-hub.com" not in href:
            external += 1
        elif "articles/" in href or href.startswith("/") or href.endswith(".html"):
            internal += 1

    if external == 0:
        issues.append("No external links (missing official source)")
    if internal < 2:
        issues.append(f"Only {internal} internal links (requires 2-4)")

    img_match = re.search(r'<img[^>]+alt=["\'](.*?)["\']', html, re.IGNORECASE)
    if img_match:
        alt = img_match.group(1)
        if not alt or "image" in alt.lower():
            issues.append("Missing or generic Image Alt text")
    elif "<img" not in html:
        issues.append("No main image found")

    if issues:
        report.append(f"--- {filename} ---")
        report.extend(f"  - {issue}" for issue in issues)

print("=== AUDIT REPORT ===")
print(f"Total articles checked: {len(FILES)}")
if not report:
    print("All articles pass the editorial criteria.")
else:
    for item in report:
        print(item)
