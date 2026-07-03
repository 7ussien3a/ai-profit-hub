#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Profit Hub - Quality Gate (Pre-publish Validator)
=====================================================
سكربت مستقل يفحص أي مقال قبل النشر أو لأغراض التدقيق الدوري.
يستخدم نفس منطق auto_publisher.validate_article لكن كأداة CLI مستقلة.

الاستخدام:
    python validate_before_publish.py articles/some-article.html
    python validate_before_publish.py --all                 # فحص كل المقالات
    python validate_before_publish.py --all --quiet         # فقط الأخطاء
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# اكتشاف تلقائي للموقع: يدعم (أ) السكربت في الجذر، (ب) داخل site/scripts/
_SCRIPT = Path(__file__).resolve().parent
if (_SCRIPT / 'site').is_dir():
    ROOT = _SCRIPT              # الحالة (أ): الجذر
    SITE = ROOT / 'site'
else:
    SITE = _SCRIPT.parent.parent  # الحالة (ب): site/scripts/ -> site/
    ROOT = SITE.parent            # مشروع قوقل ادسنس/

# ============================================================
# الفحوصات
# ============================================================
def load_config():
    cfg_path = _SCRIPT / 'publish-config.json'
    if not cfg_path.exists():
        cfg_path = ROOT / 'publish-config.json'
    if cfg_path.exists():
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'validation': {'min_word_count': 800},
            'validation_forbidden_image_domains': []}


def extract_jsonld_blocks(content):
    """استخراج كل كتل JSON-LD من المحتوى."""
    return re.findall(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
        content, re.DOTALL
    )


def validate_jsonld(content):
    """فحص صحة كل كتل JSON-LD. تُرجع (ok, errors_list)."""
    errors = []
    blocks = extract_jsonld_blocks(content)
    if not blocks:
        return False, ['no JSON-LD blocks found']
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError as e:
            errors.append(f'block {i+1}: {str(e)[:80]}')
    return (len(errors) == 0), errors


def check_links_resolve(content, base_dir):
    """فحص أن الروابط الداخلية النسبية تشير لملفات موجودة."""
    broken = []
    # روابط href نسبية لملفات .html
    for m in re.finditer(r'href="(?!https?://|#|mailto:)([^"]+\.html[^"]*)"', content):
        href = m.group(1).split('#')[0].split('?')[0]
        if href.startswith('../'):
            target = (base_dir.parent / href[3:]).resolve()
        elif href.startswith('/'):
            target = (SITE / href[1:]).resolve()
        else:
            target = (base_dir / href).resolve()
        if not target.exists():
            broken.append(href)
    return broken


def check_images_resolve(content, base_dir):
    """فحص أن الصور المحلية موجودة + لا صور خارجية ممنوعة."""
    missing = []
    external = []
    forbidden_domains = ['pollinations.ai', 'images.unsplash.com']
    # روابط src
    for m in re.finditer(r'(?:src|content)="([^"]+\.(?:jpg|jpeg|png|webp|gif|svg))"', content, re.IGNORECASE):
        src = m.group(1)
        if src.startswith('http'):
            if any(d in src for d in forbidden_domains):
                external.append(src[:80])
            continue
        if src.startswith('../'):
            target = (base_dir.parent / src[3:]).resolve()
        elif src.startswith('/'):
            target = (SITE / src[1:]).resolve()
        else:
            target = (base_dir / src).resolve()
        if not target.exists():
            missing.append(src[:80])
    return missing, external


def validate_article(filepath, config):
    """تشغيل كل الفحوصات على ملف واحد. تُرجع (passed, results_dict)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    base_dir = Path(filepath).parent

    # الفحوصات
    min_words = int(config.get('validation', {}).get('min_word_count', 800))
    text_only = re.sub(r'<[^>]+>', '', content)
    word_count = len(re.findall(r'\b\w+\b', text_only))

    jsonld_ok, jsonld_errs = validate_jsonld(content)
    broken_links = check_links_resolve(content, base_dir)
    missing_imgs, external_imgs = check_images_resolve(content, base_dir)

    results = {
        'ga_present': (
            'googletagmanager.com/gtag/js' in content,
            'Google Analytics gtag snippet'
        ),
        'canonical_present': (
            'rel="canonical"' in content,
            '<link rel="canonical">'
        ),
        'robots_indexable': (
            'index, follow' in content,
            '<meta name="robots" content="index, follow">'
        ),
        'meta_dates': (
            'article:published_time' in content and 'article:modified_time' in content,
            'article:published_time + article:modified_time'
        ),
        'jsonld_valid': (
            jsonld_ok,
            f'JSON-LD parse errors: {jsonld_errs}' if jsonld_errs else 'valid'
        ),
        'min_word_count': (
            word_count >= min_words,
            f'{word_count} words (min: {min_words})'
        ),
        'has_h1': (
            '<h1>' in content,
            '<h1> tag present'
        ),
        'no_broken_links': (
            len(broken_links) == 0,
            f'broken: {broken_links[:5]}' if broken_links else 'all resolve'
        ),
        'no_missing_images': (
            len(missing_imgs) == 0,
            f'missing: {missing_imgs[:5]}' if missing_imgs else 'all present'
        ),
        'no_external_images': (
            len(external_imgs) == 0,
            f'external forbidden: {external_imgs[:5]}' if external_imgs else 'none'
        ),
    }
    passed = all(v[0] for v in results.values())
    return passed, results


# ============================================================
# CLI
# ============================================================
def print_report(filepath, passed, results, quiet=False):
    status = '✅ PASS' if passed else '❌ FAIL'
    print(f"\n{status}  {filepath}")
    if quiet and passed:
        return
    for check, (ok, detail) in results.items():
        icon = '✅' if ok else '❌'
        print(f"  {icon} {check:22s} {detail}")


def main():
    parser = argparse.ArgumentParser(description='AI Profit Hub - Quality Gate Validator')
    parser.add_argument('file', nargs='?', help='article HTML file to validate')
    parser.add_argument('--all', action='store_true', help='validate all articles')
    parser.add_argument('--quiet', '-q', action='store_true', help='only show failures')
    args = parser.parse_args()

    config = load_config()

    if args.all:
        articles = sorted((SITE / 'articles').glob('*.html'))
        if not articles:
            print('No articles found.')
            return
        total = len(articles)
        passed_count = 0
        failures = []
        for art in articles:
            passed, results = validate_article(art, config)
            if passed:
                passed_count += 1
            else:
                failures.append((art.name, results))
                if not args.quiet:
                    print_report(art.name, False, results)
        print(f"\n{'='*50}")
        print(f"RESULTS: {passed_count}/{total} passed")
        if failures:
            print(f"FAILED ({len(failures)}):")
            for name, res in failures:
                failed_checks = [k for k, v in res.items() if not v[0]]
                print(f"  ❌ {name}: {', '.join(failed_checks)}")
        sys.exit(0 if passed_count == total else 1)

    elif args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = SITE / filepath
        if not filepath.exists():
            print(f'File not found: {filepath}')
            sys.exit(2)
        passed, results = validate_article(filepath, config)
        print_report(str(filepath), passed, results, quiet=args.quiet)
        sys.exit(0 if passed else 1)

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == '__main__':
    main()
