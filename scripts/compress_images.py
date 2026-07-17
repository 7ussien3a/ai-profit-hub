#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
compress_images.py - AI Profit Hub
====================================
يضغط جميع الصور التي يتجاوز حجمها 200KB في مجلد /images/
مع الحفاظ على الجودة البصرية وتحويل PNG إلى WebP.

الخوارزمية:
1. يبحث عن كل صورة > 200KB (JPG, PNG, WebP)
2. يحاول الضغط بجودة تنازلية حتى يصل للهدف
3. PNG → يُحوَّل إلى WebP (أصغر وأسرع)
4. JPG/WebP → يُضغط بجودة مُحسَّنة
5. يُنشئ نسخة احتياطية في images/backup/ قبل أي تعديل
6. يُولِّد تقريراً تفصيلياً في نهاية العملية
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageOps
except ImportError:
    print("❌ Pillow غير مثبت. شغّل: pip install Pillow")
    sys.exit(1)

# ─── إعدادات ──────────────────────────────────────────────────────────────────
IMAGES_DIR   = Path(__file__).parent.parent / "images"
BACKUP_DIR   = IMAGES_DIR / "backup"
MAX_SIZE_KB  = 200          # الحد الأقصى المسموح (كيلوبايت)
TARGET_KB    = 180          # الهدف الفعلي (هامش أمان 10%)
QUALITY_START = 85          # جودة البداية
QUALITY_MIN   = 55          # أدنى جودة مسموحة
QUALITY_STEP  = 5           # خطوة التخفيض
MAX_DIMENSION = 1920        # الحد الأقصى للعرض/الطول (بكسل)
EXTENSIONS    = {'.jpg', '.jpeg', '.png', '.webp'}

# ─── مساعدات ──────────────────────────────────────────────────────────────────
def size_kb(path: Path) -> float:
    return path.stat().st_size / 1024

def compress_jpg_webp(img: Image.Image, output_path: Path, target_kb: float) -> bool:
    """يضغط JPG أو WebP بجودة تنازلية حتى يصل للحجم المطلوب."""
    fmt = "WEBP" if output_path.suffix.lower() == ".webp" else "JPEG"
    for quality in range(QUALITY_START, QUALITY_MIN - 1, -QUALITY_STEP):
        import io
        buf = io.BytesIO()
        save_kwargs = {"quality": quality, "optimize": True}
        if fmt == "JPEG":
            save_kwargs["progressive"] = True
        img.save(buf, format=fmt, **save_kwargs)
        if buf.tell() / 1024 <= target_kb:
            output_path.write_bytes(buf.getvalue())
            return True
    # إذا لم يكفِ التخفيض، احفظ بأدنى جودة مسموحة
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=QUALITY_MIN, optimize=True)
    output_path.write_bytes(buf.getvalue())
    return buf.tell() / 1024 <= MAX_SIZE_KB

def png_to_webp(img: Image.Image, original_path: Path, target_kb: float) -> tuple[Path, bool]:
    """يحوّل PNG إلى WebP ويضغطه، يُرجع (المسار الجديد, نجح؟)."""
    webp_path = original_path.with_suffix(".webp")
    success = compress_jpg_webp(img, webp_path, target_kb)
    # إذا نجح التحويل، احذف PNG الأصلي
    if webp_path.exists() and size_kb(webp_path) < MAX_SIZE_KB:
        original_path.unlink()
        return webp_path, True
    return webp_path, success

def resize_if_needed(img: Image.Image) -> Image.Image:
    """يُصغِّر الصورة إذا كان أحد أبعادها يتجاوز MAX_DIMENSION."""
    w, h = img.size
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
    return img

def ensure_rgb(img: Image.Image) -> Image.Image:
    """يتأكد من أن الصورة بصيغة RGB (لحفظ JPG بشكل صحيح)."""
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode in ("RGBA", "LA"):
            background.paste(img, mask=img.split()[-1])
        return background
    return img.convert("RGB") if img.mode != "RGB" else img

# ─── المنطق الرئيسي ────────────────────────────────────────────────────────────
def process_images():
    if not IMAGES_DIR.exists():
        print(f"❌ مجلد الصور غير موجود: {IMAGES_DIR}")
        sys.exit(1)

    BACKUP_DIR.mkdir(exist_ok=True)

    # اجمع كل الصور الكبيرة
    big_images = [
        p for p in IMAGES_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in EXTENSIONS
        and size_kb(p) > MAX_SIZE_KB
        and p.name != "backup"
    ]

    if not big_images:
        print("✅ لا توجد صور تتجاوز 200KB — الموقع في حالة ممتازة!")
        return

    big_images.sort(key=lambda p: size_kb(p), reverse=True)

    print(f"\n[*] AI Profit Hub - Image Optimizer")
    print(f"{'='*60}")
    print(f"[DIR]    : {IMAGES_DIR}")
    print(f"[IMAGES] : {len(big_images)} images over {MAX_SIZE_KB}KB")
    print(f"[TARGET] : < {MAX_SIZE_KB}KB per image")
    print(f"{'='*60}\n")

    results = []
    total_saved_kb = 0

    for i, img_path in enumerate(big_images, 1):
        original_kb = size_kb(img_path)
        ext = img_path.suffix.lower()
        print(f"[{i:02d}/{len(big_images)}] {img_path.name:<55} {original_kb:>7.1f}KB -> ", end="", flush=True)

        # نسخة احتياطية
        backup_path = BACKUP_DIR / img_path.name
        if not backup_path.exists():
            shutil.copy2(img_path, backup_path)

        try:
            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)   # تصحيح الدوران
            img = resize_if_needed(img)

            new_path = img_path
            success = False

            if ext == ".png":
                # حوّل PNG → WebP
                rgb_img = ensure_rgb(img) if img.mode not in ("RGBA", "P") else img
                new_path, success = png_to_webp(rgb_img, img_path, TARGET_KB)
            elif ext in (".jpg", ".jpeg"):
                rgb_img = ensure_rgb(img)
                success = compress_jpg_webp(rgb_img, img_path, TARGET_KB)
            elif ext == ".webp":
                compress_jpg_webp(img, img_path, TARGET_KB)
                success = size_kb(img_path) <= MAX_SIZE_KB

            new_kb = size_kb(new_path)
            saved = original_kb - new_kb
            total_saved_kb += saved
            status = "[OK]" if new_kb <= MAX_SIZE_KB else "[!] "
            print(f"{new_kb:>7.1f}KB  {status}  (وفّر: {saved:+.1f}KB)")

            results.append({
                "name":        img_path.name,
                "new_name":    new_path.name,
                "original_kb": original_kb,
                "new_kb":      new_kb,
                "saved_kb":    saved,
                "success":     new_kb <= MAX_SIZE_KB,
                "converted":   new_path.name != img_path.name,
            })

        except Exception as e:
            print(f"❌ خطأ: {e}")
            results.append({
                "name": img_path.name, "new_name": img_path.name,
                "original_kb": original_kb, "new_kb": original_kb,
                "saved_kb": 0, "success": False, "converted": False,
            })

    # ─── تقرير نهائي ──────────────────────────────────────────────────────────
    success_count = sum(1 for r in results if r["success"])
    failed = [r for r in results if not r["success"]]
    converted_count = sum(1 for r in results if r["converted"])

    print(f"\n{'='*60}")
    print(f"[REPORT] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  [OK]  Compressed OK : {success_count}/{len(results)}")
    print(f"  [>>]  PNG->WebP     : {converted_count} conversions")
    print(f"  [MB]  Total saved   : {total_saved_kb/1024:.2f} MB")

    if failed:
        print(f"\n  [!] Images still over target ({len(failed)}):")
        for r in failed:
            print(f"      - {r['new_name']:<50} {r['new_kb']:.1f}KB")
        print(f"\n  [i] These need manual resize or dimension reduction.")
    else:
        print(f"\n  [DONE] All images now < {MAX_SIZE_KB}KB - Core Web Vitals ready!")

    print(f"\n  [BAK] Backups saved in: {BACKUP_DIR}")
    print(f"{'='*60}\n")

    # ─── تنبيه بالصور المحوَّلة لتحديث HTML ──────────────────────────────────
    png_converted = [r for r in results if r["converted"]]
    if png_converted:
        print(f"[!] WARNING: {len(png_converted)} PNG files converted to WebP.")
        print(f"    Update their references in HTML files:")
        for r in png_converted:
            print(f"    - {r['name']}  =>  {r['new_name']}")
        print()

if __name__ == "__main__":
    process_images()
