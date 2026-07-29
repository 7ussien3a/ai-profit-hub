import json
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"

topics = []
for path in sorted(ARTICLES.glob("*.html")):
    basename = path.name
    if basename.startswith("article") or "20260704-" in basename or "20260705-" in basename:
        continue

    soup = BeautifulSoup(
        path.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    redirect = soup.find(
        "meta",
        attrs={"http-equiv": lambda value: value and value.lower() == "refresh"},
    )
    if redirect:
        continue

    title_tag = soup.find("title")
    h1_tag = soup.find("h1")
    topics.append(
        {
            "file": path.relative_to(ROOT).as_posix(),
            "basename": basename,
            "title": title_tag.get_text(" ", strip=True)
            if title_tag
            else path.stem.replace("-", " "),
            "h1": h1_tag.get_text(" ", strip=True) if h1_tag else "",
        }
    )

(ROOT / "topics.json").write_text(
    json.dumps(topics, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(f"Extracted {len(topics)} topics")
