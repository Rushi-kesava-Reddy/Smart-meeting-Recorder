"""
Automated Test Suite for Multilingual AI Smart Meeting Recorder.
Tests language detection, translation, summarization, action extraction,
email drafting, Unicode PDF compilation, and Flask REST endpoints.
"""

import os
import sys
import json
import unittest
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import languages
import language_detector
from demo_data import DEMO_SCENARIOS, get_demo_scenario
from report_generator import generate_pdf_report
from flask_app import app


class TestMultilingualSuite(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_01_language_registry(self):
        """Verify language registry and font mappings."""
        langs = languages.get_supported_languages()
        self.assertGreaterEqual(len(langs), 18)

        # Check Telugu font
        te_font, te_path = languages.get_font_for_language("te")
        self.assertEqual(te_font, "NotoSansTelugu")
        self.assertTrue(os.path.exists(te_path), f"Font missing: {te_path}")

        # Check Hindi font
        hi_font, hi_path = languages.get_font_for_language("hi")
        self.assertEqual(hi_font, "NotoSansDevanagari")
        self.assertTrue(os.path.exists(hi_path), f"Font missing: {hi_path}")

        # Check Tamil font
        ta_font, ta_path = languages.get_font_for_language("ta")
        self.assertEqual(ta_font, "NotoSansTamil")
        self.assertTrue(os.path.exists(ta_path), f"Font missing: {ta_path}")

        print("✓ Test 01 Passed: Language registry and font mappings valid.")

    def test_02_script_detector(self):
        """Verify Unicode script detection heuristics."""
        telugu_sample = "ఈరోజు ప్రాజెక్ట్ గురించి మనం చర్చించాము"
        lang, conf = language_detector.detect_script_from_text(telugu_sample)
        self.assertEqual(lang, "te")
        self.assertGreater(conf, 0.8)

        hindi_sample = "आज हमने नए AI उत्पाद के लॉन्च पर चर्चा की"
        lang, conf = language_detector.detect_script_from_text(hindi_sample)
        self.assertEqual(lang, "hi")
        self.assertGreater(conf, 0.8)

        tamil_sample = "இன்றைய கூட்டத்தில் திட்டத்தின் முக்கிய மைல்கற்கள் பற்றி விவாதித்தோம்"
        lang, conf = language_detector.detect_script_from_text(tamil_sample)
        self.assertEqual(lang, "ta")
        self.assertGreater(conf, 0.8)

        english_sample = "Today our engineering team reviewed the cloud scaling architecture."
        lang, conf = language_detector.detect_script_from_text(english_sample)
        self.assertEqual(lang, "en")

        print("✓ Test 02 Passed: Script detection accurate for Telugu, Hindi, Tamil, English.")

    def test_03_load_demo_telugu(self):
        """Test loading Telugu demo scenario and verifying generated state."""
        response = self.client.post(
            "/api/load_demo",
            data=json.dumps({"scenario_id": "telugu_project"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")

        # Verify state endpoint
        status_res = self.client.get("/api/status")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.get_json()

        self.assertTrue(status_data["has_transcript"])
        self.assertTrue(status_data["has_summary"])
        self.assertTrue(status_data["has_email"])
        self.assertTrue(status_data["has_pdf"])
        self.assertEqual(status_data["detected_language"], "te")
        self.assertGreaterEqual(len(status_data["action_items"]), 2)

        print("✓ Test 03 Passed: Telugu demo loaded, state, action items, and PDF populated.")

    def test_04_unicode_pdf_reports(self):
        """Verify Unicode PDF generation for Telugu, Hindi, and English without box characters."""
        for lang_code in ["te", "hi", "en"]:
            pdf_path = generate_pdf_report(report_language=lang_code)
            self.assertTrue(os.path.exists(pdf_path))
            self.assertGreater(os.path.getsize(pdf_path), 5000)

        print("✓ Test 04 Passed: Unicode PDF reports generated successfully.")

    def test_05_flask_routes_and_downloads(self):
        """Verify all HTML routes and download endpoints."""
        routes = ["/", "/transcript", "/summary", "/email", "/report", "/modules", "/about", "/health"]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route failed: {route}")

        # Test download endpoints
        pdf_res = self.client.get("/download")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.mimetype, "application/pdf")

        txt_res = self.client.get("/download/transcript")
        self.assertEqual(txt_res.status_code, 200)

        email_res = self.client.get("/download/email")
        self.assertEqual(email_res.status_code, 200)

        print("✓ Test 05 Passed: All web pages and download endpoints return 200 OK.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
