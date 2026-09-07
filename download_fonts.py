import os
import urllib.request
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

FONT_URLS = {
    "NotoSans-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "NotoSansTelugu-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Regular.ttf",
    "NotoSansDevanagari-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",
    "NotoSansTamil-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf",
    "NotoSansKannada-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf",
    "NotoSansMalayalam-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansMalayalam/NotoSansMalayalam-Regular.ttf",
    "NotoSansBengali-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf",
    "NotoSansGujarati-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansGujarati/NotoSansGujarati-Regular.ttf",
    "NotoSansGurmukhi-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansGurmukhi/NotoSansGurmukhi-Regular.ttf",
    "NotoSansArabic-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf",
}

def download_fonts():
    print(f"Downloading Unicode fonts to {FONTS_DIR}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    success_count = 0

    for font_name, url in FONT_URLS.items():
        dest_path = os.path.join(FONTS_DIR, font_name)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
            print(f"  [OK] Already exists: {font_name} ({os.path.getsize(dest_path)} bytes)")
            success_count += 1
            continue

        try:
            print(f"  [>] Fetching {font_name}...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                with open(dest_path, "wb") as f:
                    f.write(data)
            print(f"  [+] Downloaded: {font_name} ({len(data)} bytes)")
            success_count += 1
        except Exception as e:
            print(f"  [!] Failed to download {font_name}: {e}", file=sys.stderr)

    print(f"Fonts ready: {success_count}/{len(FONT_URLS)}")
    return success_count

if __name__ == "__main__":
    download_fonts()
