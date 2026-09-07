"""
Language Detector Module.
Provides fast heuristic Unicode block analysis to detect Indian and foreign language scripts,
along with Groq LLM-assisted language identification for ambiguous or mixed-language text.
"""

import re
from languages import get_language_info, get_language_name

# Unicode range definitions for major language scripts
SCRIPT_RANGES = {
    "te": (0x0C00, 0x0C7F),  # Telugu
    "hi": (0x0900, 0x097F),  # Devanagari (Hindi, Marathi, Nepali)
    "ta": (0x0B80, 0x0BFF),  # Tamil
    "kn": (0x0C80, 0x0CFF),  # Kannada
    "ml": (0x0D00, 0x0D7F),  # Malayalam
    "bn": (0x0980, 0x09FF),  # Bengali / Assamese
    "gu": (0x0A80, 0x0AFF),  # Gujarati
    "pa": (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
    "ur": (0x0600, 0x06FF),  # Arabic / Urdu
    "ar": (0x0600, 0x06FF),  # Arabic
    "zh": (0x4E00, 0x9FFF),  # Chinese Han
    "ja": (0x3040, 0x30FF),  # Japanese Hiragana / Katakana
    "ko": (0xAC00, 0xD7AF),  # Korean Hangul
}


def detect_script_from_text(text):
    """
    Fast script identification using character count matching in Unicode blocks.
    Returns (language_code, confidence_ratio).
    """
    if not text or not text.strip():
        return "en", 1.0

    counts = {code: 0 for code in SCRIPT_RANGES}
    latin_count = 0
    total_letters = 0

    for char in text:
        code_pt = ord(char)
        if char.isalpha():
            total_letters += 1
            matched = False
            for lang_code, (start, end) in SCRIPT_RANGES.items():
                if start <= code_pt <= end:
                    counts[lang_code] += 1
                    matched = True
                    break
            if not matched and ('a' <= char.lower() <= 'z'):
                latin_count += 1

    if total_letters == 0:
        return "en", 1.0

    # Find highest non-Latin count
    best_lang, best_count = max(counts.items(), key=lambda x: x[1])

    # If significant non-Latin script is detected (even in code-switched text)
    if best_count > 0 and (best_count / total_letters) > 0.15:
        confidence = round(best_count / (best_count + latin_count), 2)
        return best_lang, confidence

    return "en", round(latin_count / total_letters, 2) if total_letters > 0 else 1.0
