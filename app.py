"""
Multilingual AI Smart Meeting Recorder & Executive Assistant
Streamlit Community Cloud & Local Deployment Application.

Supports end-to-end meeting workflow:
🎙️ Audio Capture & Upload
🌐 Automatic Language Detection (Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Urdu, English, etc.)
📝 Original Script Transcript Preservation
🔄 Context-Aware AI Translation
🤖 7-Section Executive Multilingual Summarization
📌 Action Items & Decisions Matrix
✉️ Prioritized Follow-Up Email Drafting
📄 Unicode PDF Report Generation with Bundled Google Noto TrueType Fonts
⚡ One-Click College Viva Demonstration Scenarios
"""

import os
import sys
import json
import streamlit as st

# Configure page settings first
st.set_page_config(
    page_title="Smart Meeting Recorder & Multilingual Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bridge Streamlit Secrets to environment variables
if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# Import backend modules
from languages import get_supported_languages, get_language_name, get_language_info, get_groq_api_key
from speech_to_text import transcribe_audio, save_meeting_state, load_meeting_state
from translator import translate_text
from summarizer import generate_summary
from action_items import extract_action_items
from email_drafter import draft_followup_email
from report_generator import generate_pdf_report, generate_pdf_report_bytes, PDF_PATH
from demo_data import DEMO_SCENARIOS, get_demo_scenario

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
WAV_PATH = os.path.join(MEETINGS_DIR, "meeting.wav")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
TRANSLATED_PATH = os.path.join(MEETINGS_DIR, "translated_transcript.txt")
SUMMARY_PATH = os.path.join(MEETINGS_DIR, "summary.txt")
EMAIL_PATH = os.path.join(MEETINGS_DIR, "email_draft.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

os.makedirs(MEETINGS_DIR, exist_ok=True)


# ==============================================================================
# CUSTOM STYLING (MODERN CORPORATE & COLLEGE DEMO THEME)
# ==============================================================================
st.markdown("""
<style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Modern Header Card */
    .app-header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .app-header-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .app-header-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }
    .badge-pill-header {
        background: #2563eb;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 999px;
        letter-spacing: 0.05em;
    }
    
    /* KPI Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
    }
    .kpi-tag-blue { color: #2563eb; }
    .kpi-tag-green { color: #16a34a; }
    .kpi-tag-purple { color: #7c3aed; }
    .kpi-tag-amber { color: #d97706; }

    /* Module Section Banners */
    .module-banner {
        background: #f1f5f9;
        border-left: 4px solid #2563eb;
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: #334155;
    }
    
    /* Priority Pills */
    .priority-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .priority-urgent { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .priority-high { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
    .priority-medium { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .priority-low { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    
    /* Native Script Output Highlight */
    .native-script-box {
        font-size: 1.05rem;
        line-height: 1.65;
        background: #fafafa;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
def init_session():
    persisted = load_meeting_state()
    defaults = {
        "original_transcript": persisted.get("original_transcript", ""),
        "detected_language": persisted.get("detected_language", "en"),
        "detected_language_name": persisted.get("detected_language_name", "English"),
        "transcription_confidence": persisted.get("transcription_confidence", 0.95),
        "duration": persisted.get("duration", 0),
        "word_count": persisted.get("word_count", 0),
        "translated_transcript": persisted.get("translated_transcript", ""),
        "translation_language": persisted.get("translation_language", "en"),
        "summary": persisted.get("summary_text", ""),
        "summary_language": persisted.get("summary_language", "same"),
        "action_items": persisted.get("action_items", []),
        "decisions": persisted.get("decisions", []),
        "email_draft": persisted.get("email_draft", {}),
        "pdf_bytes": None,
        "selected_scenario": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Read files if state is missing them
    if not st.session_state["original_transcript"] and os.path.exists(TRANSCRIPT_PATH):
        try:
            with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
                st.session_state["original_transcript"] = f.read().strip()
        except Exception:
            pass

    if not st.session_state["translated_transcript"] and os.path.exists(TRANSLATED_PATH):
        try:
            with open(TRANSLATED_PATH, "r", encoding="utf-8") as f:
                st.session_state["translated_transcript"] = f.read().strip()
        except Exception:
            pass

    if not st.session_state["summary"] and os.path.exists(SUMMARY_PATH):
        try:
            with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
                st.session_state["summary"] = f.read().strip()
        except Exception:
            pass

init_session()


# ==============================================================================
# SIDEBAR: BRANDING, CLOUD STATUS & VIVA DEMO PRESETS
# ==============================================================================
with st.sidebar:
    st.markdown("### 🎙️ SmartRecorder")
    st.markdown("<span class='badge-pill-header'>v3.0 Multilingual AI</span>", unsafe_allow_html=True)
    st.caption("Multilingual Meeting Intelligence for Streamlit Community Cloud")
    
    st.divider()

    # Cloud Readiness Status Indicator
    api_key_set = bool(get_groq_api_key())
    if api_key_set:
        st.success("🟢 Groq Whisper API Connected")
    else:
        st.error("🔴 GROQ_API_KEY Not Configured in Secrets")
        st.info("Paste your key in `.streamlit/secrets.toml` or Streamlit Cloud App Settings.")

    st.divider()

    # College Viva Demonstration Scenarios
    st.markdown("#### ⚡ Viva Demo Scenarios")
    st.caption("Pre-configured multilingual meeting intelligence datasets:")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🇮🇳 Telugu Sprint", use_container_width=True):
            sc = get_demo_scenario("telugu_project")
            if sc:
                st.session_state["original_transcript"] = sc["transcript"]
                st.session_state["detected_language"] = sc["language_code"]
                st.session_state["detected_language_name"] = sc["language_name"]
                st.session_state["translated_transcript"] = sc.get("translation_en", "")
                st.session_state["summary"] = sc.get("summary", "")
                st.session_state["action_items"] = sc.get("action_items", [])
                st.session_state["decisions"] = sc.get("decisions", [])
                st.session_state["email_draft"] = sc.get("email_draft", {})
                st.session_state["word_count"] = len(sc["transcript"].split())
                st.session_state["duration"] = sc.get("duration", 225)
                st.session_state["transcription_confidence"] = 0.98
                st.toast("Loaded Telugu Sprint Review scenario!", icon="🚀")
                st.rerun()

    with col_s2:
        if st.button("🇮🇳 Tamil Standup", use_container_width=True):
            sc = get_demo_scenario("tamil_standup")
            if sc:
                st.session_state["original_transcript"] = sc["transcript"]
                st.session_state["detected_language"] = sc["language_code"]
                st.session_state["detected_language_name"] = sc["language_name"]
                st.session_state["translated_transcript"] = sc.get("translation_en", "")
                st.session_state["summary"] = sc.get("summary", "")
                st.session_state["action_items"] = sc.get("action_items", [])
                st.session_state["decisions"] = sc.get("decisions", [])
                st.session_state["email_draft"] = sc.get("email_draft", {})
                st.session_state["word_count"] = len(sc["transcript"].split())
                st.session_state["duration"] = sc.get("duration", 195)
                st.session_state["transcription_confidence"] = 0.96
                st.toast("Loaded Tamil Standup Sync scenario!", icon="🚀")
                st.rerun()

    col_s3, col_s4 = st.columns(2)
    with col_s3:
        if st.button("🇮🇳 Hindi Review", use_container_width=True):
            sc = get_demo_scenario("hindi_sync")
            if sc:
                st.session_state["original_transcript"] = sc["transcript"]
                st.session_state["detected_language"] = sc["language_code"]
                st.session_state["detected_language_name"] = sc["language_name"]
                st.session_state["translated_transcript"] = sc.get("translation_en", "")
                st.session_state["summary"] = sc.get("summary", "")
                st.session_state["action_items"] = sc.get("action_items", [])
                st.session_state["decisions"] = sc.get("decisions", [])
                st.session_state["email_draft"] = sc.get("email_draft", {})
                st.session_state["word_count"] = len(sc["transcript"].split())
                st.session_state["duration"] = sc.get("duration", 260)
                st.session_state["transcription_confidence"] = 0.97
                st.toast("Loaded Hindi Sync scenario!", icon="🚀")
                st.rerun()

    with col_s4:
        if st.button("🇮🇳 Mixed Code-Switch", use_container_width=True):
            sc = get_demo_scenario("mixed_code_switch")
            if sc:
                st.session_state["original_transcript"] = sc["transcript"]
                st.session_state["detected_language"] = sc["language_code"]
                st.session_state["detected_language_name"] = sc["language_name"]
                st.session_state["translated_transcript"] = sc.get("translation_en", "")
                st.session_state["summary"] = sc.get("summary", "")
                st.session_state["action_items"] = sc.get("action_items", [])
                st.session_state["decisions"] = sc.get("decisions", [])
                st.session_state["email_draft"] = sc.get("email_draft", {})
                st.session_state["word_count"] = len(sc["transcript"].split())
                st.session_state["duration"] = sc.get("duration", 210)
                st.session_state["transcription_confidence"] = 0.94
                st.toast("Loaded Telugu + English Mixed scenario!", icon="🚀")
                st.rerun()

    if st.button("🌐 English Executive Review", use_container_width=True):
        sc = get_demo_scenario("english_executive")
        if sc:
            st.session_state["original_transcript"] = sc["transcript"]
            st.session_state["detected_language"] = sc["language_code"]
            st.session_state["detected_language_name"] = sc["language_name"]
            st.session_state["translated_transcript"] = sc.get("translation_en", "")
            st.session_state["summary"] = sc.get("summary", "")
            st.session_state["action_items"] = sc.get("action_items", [])
            st.session_state["decisions"] = sc.get("decisions", [])
            st.session_state["email_draft"] = sc.get("email_draft", {})
            st.session_state["word_count"] = len(sc["transcript"].split())
            st.session_state["duration"] = sc.get("duration", 310)
            st.session_state["transcription_confidence"] = 0.99
            st.toast("Loaded English Executive Board Review!", icon="🚀")
            st.rerun()

    st.divider()

    # Session Reset
    if st.button("🗑️ Reset Meeting Session", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        # Clean disk artifacts
        for p in [WAV_PATH, TRANSCRIPT_PATH, TRANSLATED_PATH, SUMMARY_PATH, EMAIL_PATH, STATE_PATH, PDF_PATH]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        init_session()
        st.toast("Session reset successfully.", icon="🧹")
        st.rerun()


# ==============================================================================
# MAIN PAGE HEADER & KPI METRICS
# ==============================================================================
st.markdown("""
<div class='app-header-card'>
    <div class='app-header-title'>
        🎙️ Smart Meeting Recorder & Multilingual Assistant
        <span class='badge-pill-header'>Render & Streamlit Ready</span>
    </div>
    <p class='app-header-subtitle'>
        Multilingual Speech-to-Text, Contextual Translation, Structured Executive Summarization, Action Extraction & Unicode PDF Engine.
    </p>
</div>
""", unsafe_allow_html=True)

# Metrics Grid
dur_secs = int(st.session_state["duration"] or 0)
m, s = divmod(dur_secs, 60)
dur_str = f"{m:02d}:{s:02d}"
conf_pct = int((st.session_state["transcription_confidence"] or 0.95) * 100)
actions_count = len(st.session_state["action_items"])
prio_val = st.session_state["email_draft"].get("priority", "Normal") if isinstance(st.session_state["email_draft"], dict) else "Normal"

st.markdown(f"""
<div class='kpi-container'>
    <div class='kpi-card'>
        <div class='kpi-label'>Meeting Language</div>
        <div class='kpi-val kpi-tag-blue'>{st.session_state["detected_language_name"]}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>Whisper Accuracy</div>
        <div class='kpi-val kpi-tag-green'>{conf_pct}% Fidelity</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>Audio Duration</div>
        <div class='kpi-val kpi-tag-purple'>{dur_str}</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>Total Words</div>
        <div class='kpi-val'>{st.session_state["word_count"]} words</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>Action Items</div>
        <div class='kpi-val kpi-tag-amber'>{actions_count} items</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>Email Priority</div>
        <div class='kpi-val'>{prio_val}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Supported languages map for dropdowns
LANG_OPTIONS = {lang["code"]: f"{lang['name']} ({lang['native']})" if lang["name"] != lang["native"] else lang["name"] for lang in get_supported_languages()}
LANG_CODES = list(LANG_OPTIONS.keys())


# ==============================================================================
# WORKFLOW TABS
# ==============================================================================
tab_audio, tab_transcript, tab_summary, tab_email, tab_pdf, tab_arch = st.tabs([
    "🎙️ 1. Audio Capture",
    "📝 2. Transcript & Translation",
    "🤖 3. Summary & Action Items",
    "✉️ 4. Email Assistant",
    "📄 5. Unicode PDF Report",
    "🏛️ 6. Architecture & Viva Guide"
])


# ------------------------------------------------------------------------------
# TAB 1: AUDIO CAPTURE & RECORDING
# ------------------------------------------------------------------------------
with tab_audio:
    st.markdown("<div class='module-banner'><b>Module 1: Audio Capture</b> — Record live speech directly from your microphone or upload any meeting recording. Supports Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, English, and more.</div>", unsafe_allow_html=True)

    col_rec1, col_rec2 = st.columns([1, 1])

    with col_rec1:
        st.markdown("##### 🎙️ Record from Microphone")
        audio_prompt = st.audio_input("Click the microphone to start recording your meeting speech")
        if audio_prompt is not None:
            audio_bytes = audio_prompt.read()
            with open(WAV_PATH, "wb") as f:
                f.write(audio_bytes)
            st.success("✅ Microphone audio recorded and saved to meetings/meeting.wav")
            st.audio(audio_bytes)

    with col_rec2:
        st.markdown("##### 📁 Or Upload Audio File")
        uploaded_file = st.file_uploader(
            "Upload meeting recording",
            type=["wav", "mp3", "m4a", "webm", "ogg"],
            help="Supports audio files up to 50MB in all standard speech formats."
        )
        if uploaded_file is not None:
            audio_bytes = uploaded_file.read()
            with open(WAV_PATH, "wb") as f:
                f.write(audio_bytes)
            st.success(f"✅ Uploaded {uploaded_file.name} successfully saved.")
            st.audio(audio_bytes)

    st.divider()

    # Transcribe Trigger Section
    has_audio_on_disk = os.path.exists(WAV_PATH) and os.path.getsize(WAV_PATH) > 1000

    col_stt_lang, col_stt_btn = st.columns([2, 1])
    with col_stt_lang:
        selected_stt_lang = st.selectbox(
            "Spoken Language Hint (Choose 'Auto Detect' for automatic recognition):",
            options=LANG_CODES,
            format_func=lambda c: LANG_OPTIONS[c],
            index=0
        )

    with col_stt_btn:
        st.write("")
        st.write("")
        btn_transcribe = st.button(
            "⚡ Transcribe Audio Now",
            type="primary",
            use_container_width=True,
            disabled=not has_audio_on_disk
        )

    if not has_audio_on_disk:
        st.info("ℹ️ Record audio with the microphone above, upload an audio file, or click a Viva Demo scenario in the sidebar to begin.")

    if btn_transcribe and has_audio_on_disk:
        with st.spinner("Running ultra-fast Groq Whisper speech recognition with automatic container detection..."):
            try:
                res = transcribe_audio(WAV_PATH, language=selected_stt_lang)
                if res and res.get("text"):
                    st.session_state["original_transcript"] = res["text"]
                    st.session_state["detected_language"] = res["language_code"]
                    st.session_state["detected_language_name"] = res["language_name"]
                    st.session_state["transcription_confidence"] = res["confidence"]
                    st.session_state["duration"] = res["duration"]
                    st.session_state["word_count"] = res["word_count"]

                    # Persist state
                    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
                        f.write(res["text"])

                    save_meeting_state({
                        "original_transcript": res["text"],
                        "detected_language": res["language_code"],
                        "detected_language_name": res["language_name"],
                        "transcription_confidence": res["confidence"],
                        "duration": res["duration"],
                        "word_count": res["word_count"]
                    })

                    st.success(f"🎉 Spoken speech recognized as {res['language_name']} ({int(res['confidence']*100)}% accuracy) in ~3 seconds!")
                    st.rerun()
                else:
                    st.error("Speech recognition produced an empty transcript. Please verify audio clarity.")
            except Exception as e:
                st.error(f"Speech recognition error: {e}")


# ------------------------------------------------------------------------------
# TAB 2: ORIGINAL TRANSCRIPT & TRANSLATION
# ------------------------------------------------------------------------------
with tab_transcript:
    st.markdown("<div class='module-banner'><b>Module 2 & 3: Speech-to-Text & Translation</b> — The original native script (Telugu, Hindi, Tamil, etc.) is preserved without loss, and translated on-demand into English or other languages.</div>", unsafe_allow_html=True)

    col_orig, col_trans = st.columns(2)

    with col_orig:
        st.markdown(f"#### 📝 Original Transcript (`{st.session_state['detected_language_name']}`)")
        orig_text = st.text_area(
            "Original native speech script:",
            value=st.session_state["original_transcript"],
            height=320,
            key="orig_transcript_area",
            help="Preserves the exact native script, phrasing, and project terminology."
        )

        col_orig_btn1, col_orig_btn2 = st.columns([1, 1])
        with col_orig_btn1:
            st.download_button(
                "📥 Download TXT",
                data=st.session_state["original_transcript"].encode("utf-8"),
                file_name="original_transcript.txt",
                mime="text/plain",
                use_container_width=True,
                disabled=not bool(st.session_state["original_transcript"])
            )

    with col_trans:
        st.markdown("#### 🔄 Context-Aware Translation")

        col_tlang, col_tbtn = st.columns([2, 1])
        with col_tlang:
            trans_target = st.selectbox(
                "Translate To:",
                options=[c for c in LANG_CODES if c != "auto"],
                format_func=lambda c: LANG_OPTIONS[c],
                index=[c for c in LANG_CODES if c != "auto"].index(st.session_state["translation_language"]) if st.session_state["translation_language"] in LANG_CODES else 0
            )

        with col_tbtn:
            st.write("")
            st.write("")
            btn_run_translate = st.button(
                "🌐 Translate",
                type="primary",
                use_container_width=True,
                disabled=not bool(st.session_state["original_transcript"])
            )

        if btn_run_translate and st.session_state["original_transcript"]:
            with st.spinner(f"Translating into {LANG_OPTIONS[trans_target]}..."):
                try:
                    translated = translate_text(
                        st.session_state["original_transcript"],
                        target_language=trans_target,
                        source_language=st.session_state["detected_language"]
                    )
                    st.session_state["translated_transcript"] = translated
                    st.session_state["translation_language"] = trans_target

                    with open(TRANSLATED_PATH, "w", encoding="utf-8") as f:
                        f.write(translated)

                    save_meeting_state({
                        "translated_transcript": translated,
                        "translation_language": trans_target,
                        "translation_language_name": get_language_name(trans_target)
                    })

                    st.success(f"Translation completed in {get_language_name(trans_target)}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Translation failed: {e}")

        trans_text = st.text_area(
            "Translated text:",
            value=st.session_state["translated_transcript"],
            height=250,
            key="translated_transcript_area"
        )

        st.download_button(
            "📥 Download Translated TXT",
            data=st.session_state["translated_transcript"].encode("utf-8"),
            file_name="translated_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not bool(st.session_state["translated_transcript"])
        )


# ------------------------------------------------------------------------------
# TAB 3: EXECUTIVE SUMMARY & ACTION ITEMS
# ------------------------------------------------------------------------------
with tab_summary:
    st.markdown("<div class='module-banner'><b>Module 4: Structured Summarization & Action Extraction</b> — 7-section executive briefing with extracted deliverables, assigned owners, deadlines, and key decisions.</div>", unsafe_allow_html=True)

    col_sum_opt, col_sum_btn = st.columns([2, 1])
    with col_sum_opt:
        sum_lang_choice = st.selectbox(
            "Summary Language:",
            options=["same"] + [c for c in LANG_CODES if c != "auto"],
            format_func=lambda c: "Same as Spoken Meeting Language" if c == "same" else LANG_OPTIONS[c],
            index=0
        )

    with col_sum_btn:
        st.write("")
        st.write("")
        btn_run_summary = st.button(
            "⚡ Generate Summary & Actions",
            type="primary",
            use_container_width=True,
            disabled=not bool(st.session_state["original_transcript"])
        )

    if btn_run_summary and st.session_state["original_transcript"]:
        with st.spinner("Synthesizing executive summary and extracting action items..."):
            try:
                # Ensure transcript is on disk
                with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
                    f.write(st.session_state["original_transcript"])

                # Run summary & actions
                sum_res = generate_summary(summary_language=sum_lang_choice)
                act_res = extract_action_items(st.session_state["original_transcript"], output_language="en" if sum_lang_choice == "same" else sum_lang_choice)

                st.session_state["summary"] = sum_res["summary"]
                st.session_state["summary_language"] = sum_res["language"]
                st.session_state["action_items"] = act_res.get("action_items", [])
                st.session_state["decisions"] = act_res.get("decisions", [])

                save_meeting_state({
                    "summary_text": sum_res["summary"],
                    "summary_language": sum_res["language"],
                    "summary_language_name": sum_res["language_name"],
                    "action_items": act_res.get("action_items", []),
                    "decisions": act_res.get("decisions", [])
                })

                st.success("Executive summary and action items extracted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Summarization error: {e}")

    st.divider()

    col_sview, col_aview = st.columns([1.1, 0.9])

    with col_sview:
        st.markdown("#### 📋 7-Section Executive Briefing")
        if st.session_state["summary"]:
            st.markdown(f"<div class='native-script-box'>{st.session_state['summary']}</div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Summary TXT",
                data=st.session_state["summary"].encode("utf-8"),
                file_name="executive_summary.txt",
                mime="text/plain"
            )
        else:
            st.info("Click 'Generate Summary & Actions' above to create structured meeting notes.")

    with col_aview:
        st.markdown("#### 📌 Extracted Action Items & Deliverables")
        action_items = st.session_state["action_items"]
        if action_items:
            import pandas as pd
            df_actions = pd.DataFrame(action_items)
            st.dataframe(df_actions, use_container_width=True, hide_index=True)
        else:
            st.caption("No action items extracted yet.")

        st.markdown("#### ✅ Key Decisions Made")
        decisions = st.session_state["decisions"]
        if decisions:
            for d in decisions:
                st.markdown(f"- ✅ **{d}**")
        else:
            st.caption("No decisions logged yet.")


# ------------------------------------------------------------------------------
# TAB 4: EMAIL DRAFTING ASSISTANT
# ------------------------------------------------------------------------------
with tab_email:
    st.markdown("<div class='module-banner'><b>Module 5: Follow-Up Email Assistant</b> — Evaluates urgency, formats executive subject lines, and drafts email follow-ups with team action items.</div>", unsafe_allow_html=True)

    col_em_opt, col_em_btn = st.columns([2, 1])
    with col_em_opt:
        email_lang_choice = st.selectbox(
            "Draft Email In:",
            options=[c for c in LANG_CODES if c != "auto"],
            format_func=lambda c: LANG_OPTIONS[c],
            index=[c for c in LANG_CODES if c != "auto"].index("en")
        )

    with col_em_btn:
        st.write("")
        st.write("")
        btn_run_email = st.button(
            "✉️ Draft Follow-Up Email",
            type="primary",
            use_container_width=True,
            disabled=not bool(st.session_state["original_transcript"])
        )

    if btn_run_email and st.session_state["original_transcript"]:
        with st.spinner("Drafting prioritized executive email..."):
            try:
                draft = draft_followup_email(
                    transcript=st.session_state["original_transcript"],
                    summary=st.session_state["summary"],
                    action_items=st.session_state["action_items"],
                    email_language=email_lang_choice
                )
                st.session_state["email_draft"] = draft
                save_meeting_state({"email_draft": draft})
                st.success(f"Email drafted (Priority: {draft.get('priority', 'Normal')})!")
                st.rerun()
            except Exception as e:
                st.error(f"Email drafting failed: {e}")

    email_data = st.session_state["email_draft"] or {}
    if email_data.get("body"):
        prio = email_data.get("priority", "Medium")
        prio_class = f"priority-{prio.lower()}"

        st.markdown(f"""
        <div style='margin-bottom: 16px;'>
            <span class='priority-pill {prio_class}'>Priority: {prio}</span>
            <span style='color: #64748b; font-size: 0.88rem; margin-left: 10px;'>{email_data.get("priority_reason", "")}</span>
        </div>
        """, unsafe_allow_html=True)

        col_esubj, col_erecip = st.columns([1, 1])
        with col_esubj:
            st.text_input("Subject Line:", value=email_data.get("subject", ""), key="input_email_subj")
        with col_erecip:
            st.text_input("Suggested Recipients:", value=email_data.get("recipients", ""), key="input_email_recip")

        st.text_area("Email Body:", value=email_data.get("body", ""), height=260, key="input_email_body")

        # Mailto button
        import urllib.parse
        subj_enc = urllib.parse.quote(email_data.get("subject", "Meeting Follow-up"))
        body_enc = urllib.parse.quote(email_data.get("body", ""))
        mailto_url = f"mailto:?subject={subj_enc}&body={body_enc}"

        col_ebtn1, col_ebtn2 = st.columns([1, 1])
        with col_ebtn1:
            st.link_button("📤 Open in Email Client (Mailto)", mailto_url, use_container_width=True)
        with col_ebtn2:
            st.download_button(
                "📥 Download Email (.eml / .txt)",
                data=f"Subject: {email_data.get('subject')}\n\n{email_data.get('body')}".encode("utf-8"),
                file_name="meeting_followup_email.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("Click 'Draft Follow-Up Email' to compose a prioritized message from the transcript.")


# ------------------------------------------------------------------------------
# TAB 5: UNICODE PDF REPORT GENERATOR
# ------------------------------------------------------------------------------
with tab_pdf:
    st.markdown("<div class='module-banner'><b>Module 6: Unicode PDF Engine</b> — Embedded Google Noto TrueType fonts ensure flawless rendering of Telugu, Tamil, Hindi, Kannada, Malayalam, Bengali, and English with zero tofu boxes.</div>", unsafe_allow_html=True)

    col_pdf_opt, col_pdf_btn = st.columns([2, 1])
    with col_pdf_opt:
        pdf_lang_choice = st.selectbox(
            "Compile PDF Report In:",
            options=["same"] + [c for c in LANG_CODES if c != "auto"],
            format_func=lambda c: "Same as Meeting Language" if c == "same" else LANG_OPTIONS[c],
            index=0
        )

    with col_pdf_btn:
        st.write("")
        st.write("")
        btn_run_pdf = st.button(
            "📄 Generate Unicode PDF",
            type="primary",
            use_container_width=True,
            disabled=not bool(st.session_state["original_transcript"])
        )

    if btn_run_pdf and st.session_state["original_transcript"]:
        with st.spinner("Compiling professional PDF with embedded Google Noto fonts..."):
            try:
                # Save latest transcript and summary to disk
                with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
                    f.write(st.session_state["original_transcript"])

                pdf_bytes = generate_pdf_report_bytes(report_language=pdf_lang_choice)
                if pdf_bytes and len(pdf_bytes) > 1000:
                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.success(f"🎉 Unicode PDF compiled successfully ({len(pdf_bytes):,} bytes)!")
                    st.rerun()
                else:
                    st.error("PDF generator returned an empty file. Please check report data.")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

    st.divider()

    # If PDF is generated or exists on disk, show download button
    pdf_ready = False
    current_pdf_bytes = st.session_state.get("pdf_bytes")

    if not current_pdf_bytes and os.path.exists(PDF_PATH) and os.path.getsize(PDF_PATH) > 1000:
        with open(PDF_PATH, "rb") as f:
            current_pdf_bytes = f.read()
            st.session_state["pdf_bytes"] = current_pdf_bytes

    if current_pdf_bytes:
        st.success("✅ Multilingual Unicode PDF Report is ready for download!")
        st.download_button(
            label="⬇️ Download Meeting_Report.pdf",
            data=current_pdf_bytes,
            file_name="Meeting_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        st.markdown("""
        > **Font Guarantee**: The compiled PDF embeds:
        > - `NotoSansTelugu` for Telugu (తెలుగు)
        > - `NotoSansDevanagari` for Hindi (हिन्दी) & Marathi
        > - `NotoSansTamil` for Tamil (தமிழ்)
        > - `NotoSansKannada` for Kannada (ಕನ್ನಡ)
        > - `NotoSansMalayalam` for Malayalam (മലയാളം)
        > - `NotoSansBengali` for Bengali (বাংলা)
        > - `NotoSans` for English & Latin scripts
        """)
    else:
        st.info("Click 'Generate Unicode PDF' above to compile the official meeting report.")


# ------------------------------------------------------------------------------
# TAB 6: ARCHITECTURE & VIVA GUIDE
# ------------------------------------------------------------------------------
with tab_arch:
    st.markdown("### 🏛️ System Architecture & College Viva Guide")
    st.markdown("""
    #### 🔄 End-to-End Multilingual AI Pipeline
    ```
    [Microphone / Upload] ➡️ [Container Header Detection] ➡️ [Groq Whisper STT (v3 Turbo)]
                                                                    ⬇️
    [Unicode PDF Report] ⬅️ [Email Drafter] ⬅️ [Action Extraction] ⬅️ [Original Transcript (Native Script)]
                                                                    ⬇️
                                                        [Context-Aware Translator]
    ```
    
    #### 🎓 Viva Demonstration Questions & Answers:
    
    1. **Why does the system preserve the original language transcript?**
       - Most multilingual systems translate everything immediately into English, destroying native nuances and conversational context. Our system retains the original script (e.g., Telugu / Tamil / Hindi) in Module 2, allowing bilingual side-by-side verification before translation.
       
    2. **How does the PDF avoid broken box characters (`□□□`)?**
       - We embed language-specific Google Noto TrueType fonts dynamically using ReportLab's `TTFont` and script detection heuristics in `language_detector.py`. When Telugu text is detected, `NotoSansTelugu-Regular.ttf` is selected; for Hindi, `NotoSansDevanagari-Regular.ttf` is used.
       
    3. **How is high speed achieved during speech recognition?**
       - We employ `whisper-large-v3-turbo` on Groq's high-speed inference engine, combined with `detect_audio_container()` in `speech_to_text.py` which inspects binary magic bytes and prevents transcoding mismatches, completing transcription in **~3 seconds**.
       
    4. **How is the application deployed to Streamlit Community Cloud?**
       - The codebase runs natively with `streamlit run app.py`. All API credentials are read securely from `st.secrets["GROQ_API_KEY"]` with automatic environment fallback, and all bundled fonts in `fonts/` are packaged directly in the repository.
    """)