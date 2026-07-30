import os
import sys
import re
from bs4 import BeautifulSoup
import json

def validate_article(html_path):
    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        return False
        
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    passed = 0
    total = 10
    
    # 1. Google Analytics
    if "G-8CSEDW0FVR" in html:
        print("[Pass] 1. Google Analytics found.")
        passed += 1
    else:
        print("[Fail] 1. Missing Google Analytics.")
        
    # 2. Canonical
    if soup.find('link', rel='canonical'):
        print("[Pass] 2. Canonical tag found.")
        passed += 1
    else:
        print("[Fail] 2. Missing Canonical tag.")
        
    # 3. Meta Robots: index, follow
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots and "index, follow" in robots.get('content', ''):
        print("[Pass] 3. Meta Robots index, follow found.")
        passed += 1
    else:
        print("[Fail] 3. Missing or incorrect Meta Robots.")
        
    # 4. article:published_time + modified_time
    pub = soup.find('meta', property='article:published_time')
    mod = soup.find('meta', property='article:modified_time')
    if pub and mod:
        print("[Pass] 4. published_time and modified_time found.")
        passed += 1
    else:
        print("[Fail] 4. Missing published_time or modified_time.")
        
    # 5. JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    valid_json = False
    for s in scripts:
        try:
            json.loads(s.string)
            valid_json = True
        except:
            pass
    if valid_json:
        print("[Pass] 5. Valid JSON-LD found.")
        passed += 1
    else:
        print("[Fail] 5. Missing or invalid JSON-LD.")
        
    # 6. Report content size without enforcing a universal word-count target.
    text = soup.get_text(separator=' ')
    words = len(text.split())
    if words > 0:
        print(f"[Pass] 6. Content body is present ({words} words).")
        passed += 1
    else:
        print("[Fail] 6. Content body is empty.")
        
    # 7. H1 present (only one)
    h1s = soup.find_all('h1')
    if len(h1s) == 1:
        print("[Pass] 7. Exactly one H1 found.")
        passed += 1
    else:
        print(f"[Fail] 7. Found {len(h1s)} H1 tags.")
        
    # 8. No broken links (just checking for empty hrefs for now)
    links = soup.find_all('a')
    broken = [a for a in links if not a.get('href') or a.get('href') == '#']
    if not broken:
        print("[Pass] 8. No obvious broken links.")
        passed += 1
    else:
        print(f"[Fail] 8. Found {len(broken)} potentially broken links.")
        
    # 9. No missing local images
    images = soup.find_all('img')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missing_imgs = []
    for img in images:
        src = img.get('src', '')
        if src.startswith('../images/'):
            img_path = os.path.join(base_dir, 'images', os.path.basename(src))
            if not os.path.exists(img_path):
                missing_imgs.append(src)
    if not missing_imgs:
        print("[Pass] 9. All local images exist.")
        passed += 1
    else:
        print(f"[Fail] 9. Missing local images: {missing_imgs}")
        
    # 10. No external Pollinations URLs
    pollinations = [img for img in images if 'pollinations.ai' in img.get('src', '')]
    if not pollinations:
        print("[Pass] 10. No external Pollinations URLs.")
        passed += 1
    else:
        print("[Fail] 10. Found external Pollinations URLs. Download locally.")
        
    print(f"\nScore: {passed}/{total}")
    if passed == total:
        print("SUCCESS: 10/10 - Ready for staging/production.")
        return True
    else:
        print("FAILED: Must fix issues to reach 10/10.")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_before_publish.py <file.html>")
        sys.exit(1)
    
    sys.exit(0 if validate_article(sys.argv[1]) else 1)
