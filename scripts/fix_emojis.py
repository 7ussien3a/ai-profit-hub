import glob
import os

replacements = {
    "âš–ï¸ ": "⚖️",
    "ðŸ”¬": "🔬",
    "ðŸš€": "🔴",
    "â€”": "—"
}

files = glob.glob("site/index.html") + glob.glob("site/articles/*.html")
fixed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    for bad, good in replacements.items():
        if bad in content:
            content = content.replace(bad, good)
            modified = True
            
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        fixed += 1
        print(f"Fixed {f}")

print(f"Fixed {fixed} files total.")
