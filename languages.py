"""
Centralized Language Registry and Configuration.
Maps language codes to human-readable names, native script representations,
and bundled Google Noto TrueType fonts for Unicode PDF report generation.
"""

import os

# Base directory for fonts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

# Supported Languages Directory
SUPPORTED_LANGUAGES = [
    {
        "code": "auto",
        "name": "Auto Detect Language",
        "native": "Auto Detect",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "en",
        "name": "English",
        "native": "English",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "te",
        "name": "Telugu",
        "native": "తెలుగు",
        "font": "NotoSansTelugu-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "hi",
        "name": "Hindi",
        "native": "हिन्दी",
        "font": "NotoSansDevanagari-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ta",
        "name": "Tamil",
        "native": "தமிழ்",
        "font": "NotoSansTamil-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "kn",
        "name": "Kannada",
        "native": "ಕನ್ನಡ",
        "font": "NotoSansKannada-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ml",
        "name": "Malayalam",
        "native": "മലയാളം",
        "font": "NotoSansMalayalam-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "bn",
        "name": "Bengali",
        "native": "বাংলা",
        "font": "NotoSansBengali-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "mr",
        "name": "Marathi",
        "native": "मराठी",
        "font": "NotoSansDevanagari-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "gu",
        "name": "Gujarati",
        "native": "ગુજરાતી",
        "font": "NotoSansGujarati-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "pa",
        "name": "Punjabi",
        "native": "ਪੰਜਾਬੀ",
        "font": "NotoSansGurmukhi-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ur",
        "name": "Urdu",
        "native": "اردو",
        "font": "NotoSansArabic-Regular.ttf",
        "direction": "rtl"
    },
    {
        "code": "or",
        "name": "Odia",
        "native": "ଓଡ଼ିଆ",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "as",
        "name": "Assamese",
        "native": "অসমীয়া",
        "font": "NotoSansBengali-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "es",
        "name": "Spanish",
        "native": "Español",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "fr",
        "name": "French",
        "native": "Français",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "de",
        "name": "German",
        "native": "Deutsch",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ar",
        "name": "Arabic",
        "native": "العربية",
        "font": "NotoSansArabic-Regular.ttf",
        "direction": "rtl"
    },
    {
        "code": "zh",
        "name": "Chinese",
        "native": "中文",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ja",
        "name": "Japanese",
        "native": "日本語",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    },
    {
        "code": "ko",
        "name": "Korean",
        "native": "한국어",
        "font": "NotoSans-Regular.ttf",
        "direction": "ltr"
    }
]

# Fast lookup dictionary
LANGUAGE_MAP = {lang["code"]: lang for lang in SUPPORTED_LANGUAGES}

# Font family name mapping for ReportLab
FONT_NAME_MAP = {
    "NotoSans-Regular.ttf": "NotoSans",
    "NotoSansTelugu-Regular.ttf": "NotoSansTelugu",
    "NotoSansDevanagari-Regular.ttf": "NotoSansDevanagari",
    "NotoSansTamil-Regular.ttf": "NotoSansTamil",
    "NotoSansKannada-Regular.ttf": "NotoSansKannada",
    "NotoSansMalayalam-Regular.ttf": "NotoSansMalayalam",
    "NotoSansBengali-Regular.ttf": "NotoSansBengali",
    "NotoSansGujarati-Regular.ttf": "NotoSansGujarati",
    "NotoSansGurmukhi-Regular.ttf": "NotoSansGurmukhi",
    "NotoSansArabic-Regular.ttf": "NotoSansArabic"
}


def get_language_info(code):
    """Return language metadata dict for a given code (or English default)."""
    if not code:
        return LANGUAGE_MAP["en"]
    code = code.lower().strip()
    return LANGUAGE_MAP.get(code, LANGUAGE_MAP["en"])


def get_language_name(code):
    """Return friendly name with native script e.g. 'Telugu (తెలుగు)'."""
    info = get_language_info(code)
    if info["code"] == "auto":
        return "Auto Detect"
    if info["code"] == "en" or info["name"] == info["native"]:
        return info["name"]
    return f"{info['name']} ({info['native']})"


def get_font_for_language(code):
    """
    Return (font_family_name, font_path) for ReportLab PDF generation.
    Falls back to NotoSans-Regular.ttf if language font is not available.
    """
    info = get_language_info(code)
    font_file = info.get("font", "NotoSans-Regular.ttf")
    font_path = os.path.join(FONTS_DIR, font_file)

    if not os.path.exists(font_path):
        # Fallback to base NotoSans
        fallback_path = os.path.join(FONTS_DIR, "NotoSans-Regular.ttf")
        if os.path.exists(fallback_path):
            return "NotoSans", fallback_path
        return "Helvetica", None

    family_name = FONT_NAME_MAP.get(font_file, "NotoSans")
    return family_name, font_path


def get_supported_languages():
    """Return list of all supported languages for API and UI dropdowns."""
    return SUPPORTED_LANGUAGES


def get_groq_api_key():
    """
    Retrieve Groq API key safely from Streamlit Secrets or Environment Variables.
    Works seamlessly on both Streamlit Community Cloud and local environments.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")

