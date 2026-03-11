"""
AI Fake News Detector PRO — FastAPI Backend
Powered by Google Gemini AI + ML Heuristics
Author: Built for Resume / Portfolio Project
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
from pypdf import PdfReader

from backend.gemini_service import analyze_text, analyze_image
from backend.url_scraper import extract_from_url
from backend.models import TextRequest, URLRequest
from ml.text_analyzer import ml_analyze

# ── App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="🔍 AI Fake News Detector PRO",
    description="""
## AI-Powered Fake News Detection API

Built with **Google Gemini AI** + **ML Heuristics**

### Features:
- 📝 Analyze pasted article text
- 🔗 Analyze articles from URLs
- 📁 Analyze uploaded .txt and .pdf files
- 🖼️ Analyze images for manipulation/deepfakes
- 🤖 ML heuristic scoring layer
- 📊 Detailed credibility breakdown
- 📄 Export analysis reports

### Models Used:
- Google Gemini 1.5 Flash (Text + Image)
- Custom ML heuristic analyzer
    """,
    version="2.0.0",
    contact={
        "name": "Fake News Detector PRO",
        "url": "http://localhost:8501"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ────────────────────────────────────────────────────

def extract_pdf_text(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        reader = PdfReader(tmp_path)
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
    finally:
        os.unlink(tmp_path)
    return text[:12000]


def build_full_result(gemini_result: dict, text: str, source_override: str = None) -> dict:
    """Merge Gemini result with ML analysis."""
    ml_score, language_tone, clickbait_score, source_credibility = ml_analyze(text)

    gemini_result["ml_score"] = ml_score
    gemini_result["language_tone"] = language_tone
    gemini_result["clickbait_score"] = clickbait_score

    # Only override source_credibility if we have a better signal
    if source_override and source_override != "Unknown":
        gemini_result["source_credibility"] = source_override
    else:
        gemini_result["source_credibility"] = source_credibility

    return gemini_result


# ── Routes ────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    return {
        "message": "🔍 AI Fake News Detector PRO is running!",
        "version": "2.0.0",
        "powered_by": ["Google Gemini 1.5 Flash", "ML Heuristics"],
        "endpoints": {
            "text":    "POST /analyze/text",
            "url":     "POST /analyze/url",
            "file":    "POST /analyze/file",
            "image":   "POST /analyze/image",
            "health":  "GET  /health",
            "docs":    "GET  /docs"
        }
    }


@app.get("/health", tags=["General"])
def health_check():
    api_key = os.getenv("GEMINI_API_KEY", "")
    return {
        "status": "✅ Online",
        "gemini_configured": bool(api_key),
        "model_text": "gemini-1.5-flash-latest",
        "model_image": "gemini-1.5-flash-latest",
        "features": [
            "text_analysis",
            "url_analysis",
            "file_analysis",
            "image_analysis",
            "ml_heuristics",
            "pdf_export"
        ]
    }


@app.post("/analyze/text", tags=["Analysis"])
def analyze_text_endpoint(req: TextRequest):
    """
    Analyze pasted article text for fake news.

    - Minimum 50 characters required
    - Returns verdict, confidence, credibility score, reasons, red flags
    """
    text = req.text.strip()
    if len(text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Article too short. Please paste at least 50 characters."
        )

    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text)

    return {
        "source": "text",
        "characters_analyzed": len(text),
        "result": full_result
    }


@app.post("/analyze/url", tags=["Analysis"])
def analyze_url_endpoint(req: URLRequest):
    """
    Fetch article from a URL and analyze for fake news.

    - Automatically extracts article text from the webpage
    - Checks domain credibility (BBC, Reuters = high trust)
    - Returns full analysis
    """
    text, domain_credibility = extract_from_url(req.url)
    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text, source_override=domain_credibility)

    return {
        "source": "url",
        "url": req.url,
        "domain_credibility": domain_credibility,
        "characters_analyzed": len(text),
        "result": full_result
    }


@app.post("/analyze/file", tags=["Analysis"])
def analyze_file_endpoint(file: UploadFile = File(...)):
    """
    Upload a .txt or .pdf file and analyze for fake news.

    - Supports: .txt and .pdf files
    - PDF text is automatically extracted
    - Returns full analysis
    """
    filename = file.filename.lower()

    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .pdf files are supported."
        )

    content = file.file.read()

    if filename.endswith(".pdf"):
        text = extract_pdf_text(content)
    else:
        text = content.decode("utf-8", errors="replace")

    text = text.strip()
    if len(text) < 50:
        raise HTTPException(
            status_code=400,
            detail="File content too short to analyze. Minimum 50 characters needed."
        )

    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text)

    return {
        "source": "file",
        "filename": file.filename,
        "characters_analyzed": len(text),
        "result": full_result
    }


@app.post("/analyze/image", tags=["Analysis"])
def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Upload an image to detect manipulation, deepfakes, or AI-generated content.

    - Supports: .jpg, .jpeg, .png, .webp
    - Uses Gemini Vision AI
    - Detects deepfakes, AI-generated images, photo manipulation
    """
    filename = file.filename.lower()
    allowed = [".jpg", ".jpeg", ".png", ".webp"]

    if not any(filename.endswith(ext) for ext in allowed):
        raise HTTPException(
            status_code=400,
            detail="Only .jpg, .jpeg, .png, and .webp images are supported."
        )

    content = file.file.read()

    # Determine mime type
    if filename.endswith(".png"):
        mime = "image/png"
    elif filename.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    gemini_result = analyze_image(content, mime)

    return {
        "source": "image",
        "filename": file.filename,
        "result": gemini_result
    }
