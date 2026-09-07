"""
Pre-configured Multilingual Demonstration Datasets for Viva / College Demo.
Provides sample meeting transcripts in Telugu, Hindi, Tamil, Mixed Telugu-English, and English.
"""

DEMO_SCENARIOS = {
    "telugu_project": {
        "id": "telugu_project",
        "title": "Telugu - Software Engineering Sprint Review",
        "language_code": "te",
        "language_name": "Telugu (తెలుగు)",
        "duration": 225,
        "transcript": (
            "ఈరోజు మన ప్రాజెక్ట్ స్ప్రింట్ సమీక్ష ప్రారంభమైంది. రవి ఫ్రంటెండ్ UI కాంపోనెంట్స్ మరియు "
            "రెస్పాన్సివ్ డిజైన్ దాదాపు పూర్తి చేసారు. ప్రియా డేటాబేస్ మైగ్రేషన్ మరియు API ఎండ్ పాయింట్స్ "
            "రేపటిలోగా పూర్తి చేయాలి. సురేష్ సెక్యూరిటీ ఆడిట్ మరియు లోడ్ టెస్టింగ్ నిర్వహిస్తున్నారు. "
            "మనం వచ్చే శుక్రవారం లోగా క్లౌడ్ డిప్లాయ్మెంట్ పూర్తి చేసి క్లయింట్ డెమో ఇవ్వాలని నిర్ణయించాము. "
            "ఏమైనా సమస్యలు ఉంటే వెంటనే టీమ్ స్లాక్ ఛానెల్ లో తెలియజేయండి."
        ),
        "translation_en": (
            "Today our project sprint review has commenced. Ravi has almost completed the frontend UI "
            "components and responsive design. Priya must complete the database migration and API endpoints "
            "by tomorrow. Suresh is conducting security audits and load testing. We have decided to complete "
            "the cloud deployment by next Friday and conduct the client demonstration. If there are any blockers, "
            "please report them immediately in the team Slack channel."
        ),
        "summary": (
            "1. Executive Summary\n"
            "ప్రాజెక్ట్ స్ప్రింట్ పురోగతి సమీక్ష జరిగింది. ఫ్రంటెండ్ దాదాపు పూర్తయింది మరియు వచ్చే శుక్రవారం డెమో నిర్వహించబడుతుంది.\n\n"
            "2. Key Discussion Points\n"
            "- ఫ్రంటెండ్ రెస్పాన్సివ్ డిజైన్ పనితీరు.\n"
            "- డేటాబేస్ మైగ్రేషన్ మరియు API అభివృద్ధి స్థితి.\n"
            "- సెక్యూరిటీ ఆడిట్ మరియు లోడ్ టెస్టింగ్ ప్రణాళిక.\n\n"
            "3. Decisions Made\n"
            "- వచ్చే శుక్రవారం లోగా క్లౌడ్ డిప్లాయ్మెంట్ పూర్తి చేసి క్లయింట్ డెమో నిర్వహించాలి.\n\n"
            "4. Action Items\n"
            "- రవి: ఫ్రంటెండ్ UI కాంపోనెంట్స్ ఖరారు చేయండి\n"
            "- ప్రియా: డేటాబేస్ మైగ్రేషన్ మరియు API ఎండ్ పాయింట్స్ పూర్తి చేయండి\n"
            "- సురేష్: సెక్యూరిటీ ఆడిట్ మరియు లోడ్ టెస్టింగ్ నిర్వహించండి\n\n"
            "5. Important Deadlines\n"
            "- రేపు సాయంత్రం: డేటాబేస్ మైగ్రేషన్ పూర్తి\n"
            "- వచ్చే శుక్రవారం: క్లౌడ్ డిప్లాయ్మెంట్ మరియు క్లయింట్ డెమో\n\n"
            "6. Important People\n"
            "- రవి, ప్రియా, సురేష్\n\n"
            "7. Next Steps\n"
            "- శుక్రవారం ఉదయం ప్రీ-డెమో సమీక్ష సమావేశం."
        ),
        "action_items": [
            {
                "task": "ఫ్రంటెండ్ UI కాంపోనెంట్స్ ఖరారు చేయండి",
                "assigned_to": "రవి",
                "deadline": "ఈరోజు సాయంత్రం",
                "priority": "High",
                "status": "In Progress"
            },
            {
                "task": "డేటాబేస్ మైగ్రేషన్ & API ఎండ్ పాయింట్స్ పూర్తి చేయండి",
                "assigned_to": "ప్రియా",
                "deadline": "రేపు",
                "priority": "High",
                "status": "Pending"
            },
            {
                "task": "సెక్యూరిటీ ఆడిట్ మరియు లోడ్ టెస్టింగ్",
                "assigned_to": "సురేష్",
                "deadline": "గురువారం",
                "priority": "Medium",
                "status": "Pending"
            }
        ],
        "decisions": [
            "వచ్చే శుక్రవారం లోగా క్లౌడ్ డిప్లాయ్మెంట్ పూర్తి చేసి క్లయింట్ డెమో నిర్వహించాలి."
        ],
        "email_draft": {
            "subject": "Follow-up: Sprint Review & Client Demo Readiness",
            "priority": "High",
            "priority_reason": "Upcoming cloud deployment and client presentation deadline this Friday.",
            "recipients": "Ravi, Priya, Suresh, Team Leads",
            "body": (
                "Hi Team,\n\n"
                "Thank you for attending today's project sprint review. We made solid progress across the stack.\n\n"
                "Meeting Highlights & Decisions:\n"
                "• Frontend UI is nearing completion thanks to Ravi.\n"
                "• Target cloud deployment is confirmed for this Friday followed by the client demo.\n\n"
                "Key Deliverables:\n"
                "1. Ravi - Finalize remaining frontend responsive components (Today).\n"
                "2. Priya - Complete database migration and API endpoints (Tomorrow).\n"
                "3. Suresh - Execute security and load testing audit (Thursday).\n\n"
                "Please raise any impediments immediately in our team channel.\n\n"
                "Best regards,\n"
                "Project Lead"
            )
        }
    },
    "hindi_product": {
        "id": "hindi_product",
        "title": "Hindi - Product Strategy & AI Launch",
        "language_code": "hi",
        "language_name": "Hindi (हिन्दी)",
        "duration": 280,
        "transcript": (
            "नमस्ते टीम, आज की बैठक में हम नए AI मीटिंग असिस्टेंट उत्पाद के लॉन्च पर चर्चा कर रहे हैं। "
            "अमित ने बताया कि मॉडल की एक्यूरेसी 95% से अधिक पहुंच चुकी है। नेहा मार्केटिंग और सोशल मीडिया अभियान "
            "की तैयारी करेंगी। राहुल सर्वर इंफ्रास्ट्रक्चर और लोड बैलेंसिंग संभालेंगे। हमने तय किया है कि अगले सोमवार को "
            "बीटा वर्शन कॉलेज फैकल्टी और छात्रों के लिए लाइव किया जाएगा। सभी एक्शन आइटम्स को शुक्रवार शाम 5 बजे तक पूरा "
            "करना आवश्यक है।"
        ),
        "translation_en": (
            "Hello team, in today's meeting we are discussing the launch of the new AI meeting assistant product. "
            "Amit reported that model accuracy has surpassed 95%. Neha will prepare the marketing and social media campaigns. "
            "Rahul will manage server infrastructure and load balancing. We decided that the beta version will go live for college "
            "faculty and students next Monday. All action items must be completed by Friday at 5 PM."
        ),
        "summary": (
            "1. Executive Summary\n"
            "AI मीटिंग असिस्टेंट के लॉन्च की रणनीतिक समीक्षा। सोमवार को बीटा रिलीज़ तय की गई है।\n\n"
            "2. Key Discussion Points\n"
            "- मॉडल एक्यूरेसी 95% से अधिक है।\n"
            "- सोशल मीडिया और मार्केटिंग कैंपेन योजना।\n"
            "- सर्वर इंफ्रास्ट्रक्चर और लोड बैलेंसिंग।\n\n"
            "3. Decisions Made\n"
            "- आगामी सोमवार को बीटा वर्शन का लाइव लॉन्च।\n\n"
            "4. Action Items\n"
            "- अमित: मॉडल परफॉर्मेंस रिपोर्ट तैयार करें\n"
            "- नेहा: मार्केटिंग और सोशल मीडिया अभियान तैयार करें\n"
            "- राहुल: सर्वर लोड बैलेंसिंग और क्लाउड इंफ्रास्ट्रक्चर सेटअप\n\n"
            "5. Important Deadlines\n"
            "- शुक्रवार शाम 5:00 बजे: सभी कार्य पूर्ण\n"
            "- सोमवार: बीटा लाइव रिलीज़\n\n"
            "6. Important People\n"
            "- अमित, नेहा, राहुल\n\n"
            "7. Next Steps\n"
            "- सप्ताहांत में अंतिम स्टेगिंग एनवायरनमेंट टेस्ट।"
        ),
        "action_items": [
            {
                "task": "मॉडल परफॉर्मेंस व वैलिडेशन रिपोर्ट तैयार करें",
                "assigned_to": "अमित",
                "deadline": "बुधवार",
                "priority": "Medium",
                "status": "In Progress"
            },
            {
                "task": "मार्केटिंग व सोशल मीडिया अभियान तैयार करें",
                "assigned_to": "नेहा",
                "deadline": "गुरुवार",
                "priority": "High",
                "status": "Pending"
            },
            {
                "task": "सर्वर लोड बैलेंसिंग और इंफ्रास्ट्रक्चर सेटअप",
                "assigned_to": "राहुल",
                "deadline": "शुक्रवार 5 PM",
                "priority": "High",
                "status": "Pending"
            }
        ],
        "decisions": [
            "आगामी सोमवार को कॉलेज फैकल्टी और छात्रों के लिए बीटा वर्शन लाइव लॉन्च किया जाएगा।"
        ],
        "email_draft": {
            "subject": "Launch Update: AI Meeting Assistant Beta Release Next Monday",
            "priority": "High",
            "priority_reason": "Hard deadline for Monday beta launch to faculty and students.",
            "recipients": "Amit, Neha, Rahul, Engineering Team",
            "body": (
                "Hello Everyone,\n\n"
                "Thank you for participating in today's launch strategy meeting. The product is on track for our upcoming release.\n\n"
                "Decisions & Milestone:\n"
                "• Beta version will be publicly released on Monday.\n"
                "• Final testing lock is Friday at 5:00 PM.\n\n"
                "Assigned Action Items:\n"
                "1. Amit - Model accuracy and validation documentation (Wednesday).\n"
                "2. Neha - Social media and announcement materials (Thursday).\n"
                "3. Rahul - Cloud server scaling and load balancer verification (Friday).\n\n"
                "Best regards,\n"
                "Product Management"
            )
        }
    },
    "tamil_standup": {
        "id": "tamil_standup",
        "title": "Tamil - Engineering Delivery Standup",
        "language_code": "ta",
        "language_name": "Tamil (தமிழ்)",
        "duration": 195,
        "transcript": (
            "அனைவருக்கும் வணக்கம். இன்றைய கூட்டத்தில் திட்டத்தின் முக்கிய மைல்கற்கள் பற்றி விவாதித்தோம். "
            "கார்த்திக் பயனர் இடைமுகத்தை வெற்றிகரமாக முடித்துள்ளார். மீனா பின்தள ஏபிஐ சோதனையை நாளைக்குள் "
            "முடிக்க ஒப்புக்கொண்டுள்ளார். வினோத் கிளவுட் சர்வர் அமைப்பை மேற்பார்வையிடுகிறார். இறுதி தயாரிப்பு அறிக்கை "
            "வரும் வியாழக்கிழமை சமர்ப்பிக்கப்படும் என்று முடிவு செய்யப்பட்டுள்ளது."
        ),
        "translation_en": (
            "Greetings everyone. In today's meeting we discussed the primary milestones of the project. "
            "Karthik has successfully completed the user interface. Meena has agreed to finish backend API testing "
            "by tomorrow. Vinoth is overseeing the cloud server configuration. It was resolved that the final product "
            "report will be submitted this Thursday."
        ),
        "summary": (
            "1. Executive Summary\n"
            "பொறியியல் நிலை கூட்டத்தில் பயனர் இடைமுகம் முடிவடைந்துள்ளது மற்றும் வியாழன் இறுதி அறிக்கை சமர்ப்பிக்கப்படும்.\n\n"
            "2. Key Discussion Points\n"
            "- பயனர் இடைமுக மேம்பாட்டின் நிறைவு.\n"
            "- ஏபிஐ சோதனை மற்றும் தர உத்தரவாதம்.\n"
            "- கிளவுட் சர்வர் கட்டமைப்பு.\n\n"
            "3. Decisions Made\n"
            "- இறுதி திட்ட அறிக்கை வியாழக்கிழமை சமர்ப்பிக்கப்படும்.\n\n"
            "4. Action Items\n"
            "- கார்த்திக்: பயனர் இடைமுக இறுதி சரிபார்ப்பு\n"
            "- மீனா: பின்தள ஏபிஐ சோதனை முடித்தல்\n"
            "- வினோத்: கிளவுட் சர்வர் ஒருங்கிணைப்பு\n\n"
            "5. Important Deadlines\n"
            "- நாளை: ஏபிஐ சோதனை முடிவு\n"
            "- வியாழக்கிழமை: இறுதி அறிக்கை சமர்ப்பிப்பு\n\n"
            "6. Important People\n"
            "- கார்த்திக், மீனா, வினோத்\n\n"
            "7. Next Steps\n"
            "- வியாழன் காலை இறுதி சரிபார்ப்பு கூட்டம்."
        ),
        "action_items": [
            {
                "task": "பின்தள ஏபிஐ சோதனையை நிறைவு செய்தல்",
                "assigned_to": "மீனா",
                "deadline": "நாளை",
                "priority": "High",
                "status": "In Progress"
            },
            {
                "task": "கிளவுட் சர்வர் அமைப்பை சரிபார்த்தல்",
                "assigned_to": "வினோத்",
                "deadline": "புதன்கிழமை",
                "priority": "Medium",
                "status": "Pending"
            }
        ],
        "decisions": [
            "இறுதி திட்ட அறிக்கை வரும் வியாழக்கிழமை சமர்ப்பிக்கப்படும்."
        ],
        "email_draft": {
            "subject": "Standup Notes: Final Product Report Submission Due Thursday",
            "priority": "High",
            "priority_reason": "Submission deadline on Thursday for final product report.",
            "recipients": "Karthik, Meena, Vinoth, Faculty Guides",
            "body": (
                "Hi Team,\n\n"
                "Here is the summary of today's standup discussion.\n\n"
                "Key Milestone:\n"
                "• The final project report is scheduled for submission this Thursday.\n\n"
                "Action Items:\n"
                "• Meena - Complete backend API testing suite (Tomorrow).\n"
                "• Vinoth - Cloud server configuration and deployment validation (Wednesday).\n\n"
                "Best,\n"
                "Engineering Lead"
            )
        }
    },
    "mixed_code_switch": {
        "id": "mixed_code_switch",
        "title": "Mixed Telugu-English - Code-Switching Standup",
        "language_code": "te",
        "language_name": "Telugu + English (Mixed)",
        "duration": 210,
        "transcript": (
            "Hi everyone, ippudu project progress gurinchi discuss cheddam. The frontend is almost completed by Ravi. "
            "Next sprint lo database migration and Groq API integration complete cheyyali. Priya will handle the cloud deployment "
            "on Render platform. We decided that final testing deadline Friday afternoon 4 PM. Please update Jira tickets today itself."
        ),
        "translation_en": (
            "Hi everyone, let's now discuss the project progress. The frontend is almost completed by Ravi. "
            "In the next sprint, we need to complete the database migration and Groq API integration. Priya will handle "
            "the cloud deployment on the Render platform. We decided that the final testing deadline is Friday afternoon at 4:00 PM. "
            "Please update your Jira tickets today itself."
        ),
        "summary": (
            "1. Executive Summary\n"
            "Project progress update: Frontend completed, Render deployment and Groq API integration underway for Friday release.\n\n"
            "2. Key Discussion Points\n"
            "- Frontend completion by Ravi.\n"
            "- Database migration and Groq API integration in next sprint.\n"
            "- Render cloud deployment handled by Priya.\n\n"
            "3. Decisions Made\n"
            "- Final testing deadline fixed for Friday at 4:00 PM.\n\n"
            "4. Action Items\n"
            "- Ravi: Finalize frontend review\n"
            "- Priya: Render platform cloud deployment\n"
            "- Team: Update Jira tickets today\n\n"
            "5. Important Deadlines\n"
            "- Today: Update Jira tickets\n"
            "- Friday 4:00 PM: Final testing deadline\n\n"
            "6. Important People\n"
            "- Ravi, Priya\n\n"
            "7. Next Steps\n"
            "- Team sync on Friday afternoon."
        ),
        "action_items": [
            {
                "task": "Render platform cloud deployment",
                "assigned_to": "Priya",
                "deadline": "Thursday",
                "priority": "High",
                "status": "In Progress"
            },
            {
                "task": "Update all sprint Jira tickets",
                "assigned_to": "Entire Team",
                "deadline": "Today",
                "priority": "Medium",
                "status": "Pending"
            }
        ],
        "decisions": [
            "Final testing deadline is strictly set for Friday at 4:00 PM."
        ],
        "email_draft": {
            "subject": "Sprint Sync: Testing Cutoff Friday 4 PM & Deployment Status",
            "priority": "Medium",
            "priority_reason": "Standard sprint milestone with testing cutoff on Friday.",
            "recipients": "Ravi, Priya, Development Team",
            "body": (
                "Hi Team,\n\n"
                "Quick recap from our standup today:\n\n"
                "• Frontend is nearly finalized.\n"
                "• Priya is heading cloud deployment on Render.\n"
                "• Crucial deadline: Final testing concludes this Friday at 4:00 PM.\n\n"
                "Action Items:\n"
                "1. Update your Jira tickets by end of day today.\n"
                "2. Priya to verify production environment variables and SSL.\n\n"
                "Thanks,\n"
                "Project Coordinator"
            )
        }
    },
    "english_executive": {
        "id": "english_executive",
        "title": "English - Executive Board & Cloud Scaling",
        "language_code": "en",
        "language_name": "English",
        "duration": 310,
        "transcript": (
            "Welcome everyone to our Q3 technology and platform review. Today our engineering team demonstrated "
            "the new multilingual speech recognition pipeline supporting Indian regional languages. Ravi finalized the "
            "Web Audio capture interface. Anita completed the Unicode PDF generation engine with custom Noto fonts for "
            "Render deployment. We approved the migration to high-throughput cloud inferencing with a deadline of next Wednesday. "
            "The system is operating well within the 90 MB RAM targets."
        ),
        "translation_en": (
            "Welcome everyone to our Q3 technology and platform review. Today our engineering team demonstrated "
            "the new multilingual speech recognition pipeline supporting Indian regional languages. Ravi finalized the "
            "Web Audio capture interface. Anita completed the Unicode PDF generation engine with custom Noto fonts for "
            "Render deployment. We approved the migration to high-throughput cloud inferencing with a deadline of next Wednesday. "
            "The system is operating well within the 90 MB RAM targets."
        ),
        "summary": (
            "1. Executive Summary\n"
            "Review of Q3 platform upgrades: Multilingual speech recognition, Unicode PDF generation, and Render cloud optimization.\n\n"
            "2. Key Discussion Points\n"
            "- Web Audio capture and live waveform visualizer.\n"
            "- Unicode font embedding for Indian script PDF rendering.\n"
            "- Memory optimization ensuring lightweight cloud deployment under 90 MB.\n\n"
            "3. Decisions Made\n"
            "- Approved cloud inferencing architecture with rollout deadline of next Wednesday.\n\n"
            "4. Action Items\n"
            "- Anita: Finalize Unicode font packaging and Render build check\n"
            "- Ravi: Complete browser audio cross-device compatibility testing\n\n"
            "5. Important Deadlines\n"
            "- Next Wednesday: Cloud inferencing deployment\n\n"
            "6. Important People\n"
            "- Ravi, Anita\n\n"
            "7. Next Steps\n"
            "- Staging deployment validation."
        ),
        "action_items": [
            {
                "task": "Unicode font packaging and Render deployment verification",
                "assigned_to": "Anita",
                "deadline": "Tuesday",
                "priority": "High",
                "status": "In Progress"
            },
            {
                "task": "Browser audio cross-device compatibility testing",
                "assigned_to": "Ravi",
                "deadline": "Next Monday",
                "priority": "Medium",
                "status": "Pending"
            }
        ],
        "decisions": [
            "Approved migration to high-throughput cloud inferencing with a deadline of next Wednesday."
        ],
        "email_draft": {
            "subject": "Executive Review Summary: Multilingual Engine & Production Deployment",
            "priority": "High",
            "priority_reason": "Board milestone approving next Wednesday's production rollout.",
            "recipients": "Anita, Ravi, Engineering Board",
            "body": (
                "Dear Stakeholders,\n\n"
                "Thank you for attending today's executive architecture review. We demonstrated the full multilingual pipeline with Indian script rendering and memory efficiency.\n\n"
                "Key Decisions:\n"
                "• Full deployment approved for next Wednesday.\n"
                "• System memory validated under 90 MB on Render free tier.\n\n"
                "Action Items:\n"
                "• Anita: Verify font bundle integrity during CI/CD build.\n"
                "• Ravi: Finalize microphone audio capture across browsers.\n\n"
                "Sincerely,\n"
                "Director of Technology"
            )
        }
    }
}


def get_demo_scenario(scenario_id):
    """Retrieve demo scenario by ID or default to Telugu."""
    return DEMO_SCENARIOS.get(scenario_id, DEMO_SCENARIOS["telugu_project"])


def get_all_demo_scenarios():
    """Return list of scenarios for UI selection."""
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "language_code": s["language_code"],
            "language_name": s["language_name"],
            "words": len(s["transcript"].split())
        }
        for s in DEMO_SCENARIOS.values()
    ]
