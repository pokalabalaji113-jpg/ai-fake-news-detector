# 🔍 AI Fake News Detector PRO

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=for-the-badge&logo=streamlit)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-orange?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**Detect fake news, deepfakes, and misinformation instantly using Google Gemini 2.5 Flash AI + ML Heuristics**

[Features](#features) • [Demo](#demo) • [Installation](#installation) • [Usage](#usage) • [API](#api-docs) • [Tech Stack](#tech-stack)

</div>

---

## 📌 About The Project

AI Fake News Detector PRO is a full-stack GenAI application that uses **Google Gemini 2.5 Flash** to analyze news articles and detect misinformation in real time. It supports multiple input types including text, URLs, PDF files, and images.

Built as a portfolio project to demonstrate skills in **Generative AI**, **FastAPI**, **Streamlit**, and **ML/NLP**.

---

## ✨ Features

- 📝 **Text Analysis** — Paste any news article and get instant AI verdict
- 🔗 **URL Analysis** — Enter a news URL and the app auto-fetches and analyzes it
- 📁 **File Upload** — Upload `.txt` or `.pdf` files for analysis
- 🖼️ **Image / Deepfake Detection** — Detect manipulated images and AI-generated deepfakes
- 🤖 **ML Heuristic Scoring** — Extra NLP layer for clickbait and tone detection
- 📊 **Analytics Dashboard** — Session stats, charts, and history
- 📄 **PDF Report Export** — Download full analysis report as PDF
- 🌙 **Beautiful Dark UI** — Modern responsive interface

---

## 🎯 How It Works

```
User Input (Text / URL / File / Image)
        ↓
Streamlit Frontend (localhost:8501)
        ↓
FastAPI Backend (localhost:8000)
        ↓
ML Heuristic Analyzer (clickbait, tone, red flags)
        ↓
Google Gemini 2.5 Flash AI (deep analysis)
        ↓
Result: REAL ✅ or FAKE 🚫 with full explanation
```

---

## 🖥️ Demo

### Verdict Screen
```
🚫 FAKE
Confidence: 95% | Credibility: 12/100
Language Tone: Sensational | Clickbait Score: 75

Red Flags:
🚩 Uses fear-based language to manipulate readers
🚩 No named sources or verifiable facts
🚩 Calls to share urgently before deletion
```

### Real News Detection
```
✅ REAL
Confidence: 92% | Credibility: 88/100
Language Tone: Neutral / Professional

Positive Signals:
✔ Cites named sources and official statements
✔ Writing style matches professional journalism
✔ Claims are factually consistent
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Google Gemini API Key (free from [aistudio.google.com](https://aistudio.google.com/app/apikey))

### Step 1 — Clone the repo
```bash
git clone https://github.com/pokalabalaji113-jpg/ai-fake-news-detector.git
cd ai-fake-news-detector/fake_news_pro
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
pip install google-genai
```

### Step 3 — Set up API key
```bash
cp .env.example .env
```
Open `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 4 — Run the app

**Terminal 1 — Backend:**
```bash
python run.py
```

**Terminal 2 — Frontend:**
```bash
streamlit run frontend/app.py --server.port 8501
```

### Step 5 — Open in browser
```
http://localhost:8501
```

---

## 📡 API Docs

FastAPI Swagger UI available at:
```
http://localhost:8000/docs
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status check |
| GET | `/health` | Gemini connection check |
| POST | `/analyze/text` | Analyze pasted article text |
| POST | `/analyze/url` | Analyze article from URL |
| POST | `/analyze/file` | Analyze .txt or .pdf file |
| POST | `/analyze/image` | Detect deepfakes and manipulation |

### Sample Request
```json
POST /analyze/text
{
  "text": "Your news article text here..."
}
```

### Sample Response
```json
{
  "source": "text",
  "result": {
    "verdict": "FAKE",
    "confidence": 95,
    "credibility_score": 12,
    "summary": "This article shows multiple signs of misinformation...",
    "reasons": ["No named sources", "Sensational language", "Unverifiable claims"],
    "red_flags": ["Urges sharing before deletion", "Fear-based manipulation"],
    "positive_signals": [],
    "category": "Health",
    "recommendation": "Do not share this article. Verify with trusted sources.",
    "ml_score": 0.87,
    "language_tone": "Sensational",
    "clickbait_score": 75
  }
}
```

---

## 🗂️ Project Structure

```
fake_news_pro/
│
├── backend/
│   ├── main.py              ← FastAPI app (all routes)
│   ├── gemini_service.py    ← Google Gemini AI logic
│   ├── url_scraper.py       ← URL article fetcher
│   └── models.py            ← Pydantic schemas
│
├── frontend/
│   └── app.py               ← Streamlit UI
│
├── ml/
│   └── text_analyzer.py     ← ML heuristic scoring
│
├── uploads/                 ← Temp uploaded files
├── run.py                   ← Start backend server
├── requirements.txt         ← Dependencies
├── .env.example             ← API key template
└── .gitignore               ← Protects .env file
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Google Gemini 2.5 Flash |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| ML/NLP | Custom heuristic analyzer |
| PDF Parse | pypdf |
| Web Scraping | BeautifulSoup4 |
| Charts | Plotly |
| PDF Export | ReportLab |
| Language | Python 3.10+ |

---

## 🔐 Security

- API key stored in `.env` file (never committed to GitHub)
- `.gitignore` blocks `.env` from being uploaded
- All file uploads are processed in memory and deleted after analysis

---

## 📈 Skills Demonstrated

- ✅ Generative AI / LLM Integration
- ✅ REST API Development
- ✅ Full Stack Python Development
- ✅ ML / NLP Concepts
- ✅ Prompt Engineering
- ✅ Image Analysis / Computer Vision
- ✅ Data Visualization
- ✅ PDF Generation

---

## 👨‍💻 Author

**Pokala Balaji**
- GitHub: [@pokalabalaji113-jpg](https://github.com/pokalabalaji113-jpg)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
Built with ❤️ using Google Gemini AI · FastAPI · Streamlit
</div>
