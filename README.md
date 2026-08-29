# 🎙️ Smart Meeting Recorder - Production Ready & Cloud Deployment Guide

Smart Meeting Recorder is an AI-powered web application built with Python Flask, HTML5 Web Audio API, OpenAI Whisper, and ReportLab for meeting audio recording, automated speech-to-text transcription, summarization, and PDF report generation.

---

## 📁 Updated Project Structure

```text
SmartMeetingRecorder/
│
├── app.py                     # Main Flask web application & REST API routes
├── recorder.py                # Hardware microphone recorder module (Local fallback)
├── speech_to_text.py          # OpenAI Whisper speech-to-text transcription module
├── summarizer.py              # Meeting content summarization module
├── report_generator.py        # ReportLab PDF report creation module
├── main.py                    # CLI workflow orchestration script
│
├── static/                    # Frontend static assets
│   ├── css/style.css          # Application custom styles
│   ├── js/script.js           # Client-side audio recording, visualization & API calls
│   └── images/                # Logo and graphics
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Core layout template
│   ├── index.html             # Audio Recorder Dashboard (Module 1)
│   ├── transcript.html        # Speech to Text View (Module 2)
│   ├── summary.html           # Summary Dashboard (Module 3)
│   ├── report.html            # PDF Report Download (Module 4)
│   ├── modules.html           # Architecture breakdown
│   └── about.html             # Project details
│
├── meetings/                  # Output directory for dynamic meeting files
│   └── .gitkeep               # Directory tracker for Git
│
├── Procfile                   # Gunicorn WSGI startup process config for Render / Heroku
├── requirements.txt           # Production Python dependencies
├── .env.example               # Template for environment variables
├── .gitignore                 # Excluded files for security and clean repository
└── README.md                  # Comprehensive deployment and setup guide
```

---

## 📝 Files Created / Modified

- **`app.py`**: Added production host binding (`0.0.0.0`), environment variable integration (`python-dotenv`), `/health` health-check route, and production-safe error handlers.
- **`Procfile`**: Created with Gunicorn startup command `web: gunicorn app:app`.
- **`requirements.txt`**: Added `gunicorn` and `python-dotenv`.
- **`.env.example`**: Created template for environment variables (`SECRET_KEY`, `PORT`, `FLASK_DEBUG`).
- **`.gitignore`**: Added rule to exclude local `.env`, virtual environments, pycache, and dynamic files inside `meetings/*`.
- **`meetings/.gitkeep`**: Created to ensure directory structure exists on fresh git clones.
- **`README.md`**: Detailed deployment instructions.

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory for local development by copying `.env.example`:

```bash
cp .env.example .env
```

| Variable | Recommended Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *random 32-char string* | Secret key for Flask session security |
| `HOST` | `0.0.0.0` | Server host binding (`0.0.0.0` allows external access) |
| `PORT` | `5000` | Port for web server (`Render` sets this automatically) |
| `FLASK_DEBUG` | `False` | Debug mode (Set to `False` in production) |

---

## 🚀 Local Development Setup

### 1. Install Dependencies

Open your terminal or command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

### 2. Run Flask Server Locally

```bash
python app.py
```

The app will start at `http://localhost:5000` (or `http://127.0.0.1:5000`).

### 3. Test Production WSGI Server Locally with Gunicorn (Linux/macOS/WSL)

```bash
gunicorn app:app
```

---

## ☁️ Deployment Guide (Render)

Follow these steps to deploy your Smart Meeting Recorder to **Render** so it can be accessed from any laptop, mobile phone, or internet connection over secure HTTPS.

### Step 1: Upload Code to GitHub

1. Open your terminal in the project directory.
2. Initialize git and commit your files:

```bash
git init
git add .
git commit -m "Make Smart Meeting Recorder production-ready for Render deployment"
```

3. Create a new repository on [GitHub](https://github.com/new).
4. Link your local repository to GitHub and push:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SmartMeetingRecorder.git
git push -u origin main
```

---

### Step 2: Create Web Service on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository (`SmartMeetingRecorder`).
4. Configure the Web Service settings as follows:

| Setting | Value |
| :--- | :--- |
| **Name** | `smart-meeting-recorder` (or your preferred app name) |
| **Region** | Select closest region (e.g., Oregon, Frankfurt, Singapore) |
| **Branch** | `main` |
| **Root Directory** | Leave blank |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

---

### Step 3: Configure Environment Variables on Render

In your Render Web Service dashboard:
1. Go to **Environment** tab.
2. Add the following Environment Variables:

- `SECRET_KEY`: *[Enter a strong random string]*
- `FLASK_DEBUG`: `False`

*(Note: `PORT` is automatically managed by Render)*

3. Click **Save Changes** and deploy!

---

## 🌐 Health Check & Verification

Once deployed, Render provides a public HTTPS URL like:

`https://smart-meeting-recorder.onrender.com`

### Health Check Endpoint
Verify your service health by visiting:

`https://smart-meeting-recorder.onrender.com/health`

It should return:
```json
{
  "status": "ok",
  "service": "Smart Meeting Recorder",
  "message": "Service is healthy and running"
}
```

---

## 📱 Testing from Mobile Devices & External Wi-Fi Networks

1. Open any browser (Chrome, Safari, Firefox, Edge) on any mobile phone, tablet, or secondary laptop connected to a different Wi-Fi or cellular data (4G/5G).
2. Navigate to your public Render HTTPS URL: `https://smart-meeting-recorder.onrender.com`.
3. Allow browser microphone access when prompted.
4. Click **Start Recording**, record audio, and test the full 4-step workflow:
   - **Step 1**: Audio Recording (Saved to server)
   - **Step 2**: Speech-to-Text Transcription (OpenAI Whisper)
   - **Step 3**: Summary Generation
   - **Step 4**: PDF Report Download

---

## 💾 Cloud Storage & Database Architecture Notes

### 1. File & Media Storage
- **Current Behavior**: Recordings, transcripts, and PDF reports are written to the local `./meetings` directory.
- **Cloud Considerations**: Free cloud hosting instances (such as Render) have ephemeral filesystems; files reset on container restart/redeploy.
- **Production Storage Solution**: For long-term persistent storage across sessions and scaling, integrate object storage services such as **AWS S3**, **Cloudinary**, or **Supabase Storage** to save `.wav` audio files and generated `.pdf` reports.

### 2. Database Suitability
- **Current Behavior**: The application is stateful via file outputs (`meetings/`) without a SQL database.
- **Production Database Solution**: If user accounts, multi-tenant meeting history, or multi-user audio logs are added in the future, connect a managed cloud PostgreSQL database such as **Render PostgreSQL** or **Supabase PostgreSQL**.

---

## 🔒 Security Summary

- No hardcoded local IP addresses (`127.0.0.1`) or `localhost` URLs in frontend API requests.
- All client requests use relative URLs (`/api/...`).
- No hardcoded secrets or Windows file paths (`C:\Users\...`).
- SSL/HTTPS encryption automatically handled by Render.
- Clean error handling prevents stack trace disclosure to users.
