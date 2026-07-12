import os
import glob
from bs4 import BeautifulSoup
import json

articles_dir = r"c:\Users\Admin\Desktop\X\مشروع قوقل ادسنس\site\articles"
html_files = glob.glob(os.path.join(articles_dir, "*.html"))
topics = []

for file in html_files:
    basename = os.path.basename(file)
    if basename.startswith("article") or "20260704-" in basename or "20260705-" in basename:
        continue # skip new articles or weird dated ones if we want, actually let's parse all that don't have Redirecting
    
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "Redirecting..." in content:
        continue
        
    soup = BeautifulSoup(content, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.text if title_tag else basename.replace(".html", "").replace("-", " ")
    
    h1_tag = soup.find("h1")
    h1 = h1_tag.text if h1_tag else ""
    
    topics.append({
        "file": file,
        "basename": basename,
        "title": title,
        "h1": h1
    })

with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(topics)} topics")
