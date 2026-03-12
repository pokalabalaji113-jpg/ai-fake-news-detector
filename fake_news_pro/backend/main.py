"""
AI Fake News Detector PRO — FastAPI Backend
Full CRUD for Text, URL, File, Image categories
Powered by Google Gemini AI + ML Heuristics
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from datetime import datetime
from pypdf import PdfReader

from backend.gemini_service import analyze_text, analyze_image
from backend.url_scraper import extract_from_url
from ml.text_analyzer import ml_analyze

# ── App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="🔍 AI Fake News Detector PRO",
    description="""
## AI Fake News Detector — Full CRUD REST API

Full **CRUD operations** for each input type:

| Category | POST | GET | PUT | DELETE |
|----------|------|-----|-----|--------|
| Text     | ✅   | ✅  | ✅  | ✅     |
| URL      | ✅   | ✅  | ✅  | ✅     |
| File     | ✅   | ✅  | -   | ✅     |
| Image    | ✅   | ✅  | -   | ✅     |

Powered by **Google Gemini 2.5 Flash + ML Heuristics**
    """,
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-Memory Storage (acts like a database) ──────────────────
text_store   = {}   # stores text analyses
url_store    = {}   # stores url analyses
file_store   = {}   # stores file analyses
image_store  = {}   # stores image analyses

# ── Separate counters per category ────────────────────────────
counters = {
    "text":  0,   # text:  1, 2, 3, 4, 5...
    "url":   0,   # url:   1, 2, 3, 4, 5...
    "file":  0,   # file:  1, 2, 3, 4, 5...
    "image": 0    # image: 1, 2, 3, 4, 5...
}

def next_id(category: str) -> int:
    counters[category] += 1
    return counters[category]

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
    ml_score, language_tone, clickbait_score, source_credibility = ml_analyze(text)
    gemini_result["ml_score"] = ml_score
    gemini_result["language_tone"] = language_tone
    gemini_result["clickbait_score"] = clickbait_score
    gemini_result["source_credibility"] = source_override if source_override else source_credibility
    return gemini_result


# ══════════════════════════════════════════════════════════════
#  GENERAL ROUTES
# ══════════════════════════════════════════════════════════════

@app.get("/", tags=["General"])
def root():
    return {
        "message": "🔍 AI Fake News Detector PRO v3.0",
        "powered_by": "Google Gemini 2.5 Flash + ML",
        "crud_support": ["text", "url", "file", "image"]
    }

@app.get("/health", tags=["General"])
def health():
    api_key = os.getenv("GEMINI_API_KEY", "")
    return {
        "status": "✅ Online",
        "gemini_configured": bool(api_key),
        "model": "gemini-2.5-flash",
        "total_analyses": sum(counters.values()),
        "counters": {
            "text":  counters["text"],
            "url":   counters["url"],
            "file":  counters["file"],
            "image": counters["image"]
        }
    }

@app.get("/all", tags=["General"])
def get_all_analyses():
    """Get ALL saved analyses across all categories."""
    return {
        "text_analyses":  len(text_store),
        "url_analyses":   len(url_store),
        "file_analyses":  len(file_store),
        "image_analyses": len(image_store),
        "total":          len(text_store) + len(url_store) + len(file_store) + len(image_store),
        "data": {
            "text":  list(text_store.values()),
            "url":   list(url_store.values()),
            "file":  list(file_store.values()),
            "image": list(image_store.values())
        }
    }

@app.delete("/all", tags=["General"])
def delete_all_analyses():
    """Delete ALL analyses from all categories."""
    counts = {
        "text":  len(text_store),
        "url":   len(url_store),
        "file":  len(file_store),
        "image": len(image_store)
    }
    text_store.clear()
    url_store.clear()
    file_store.clear()
    image_store.clear()
    counters["text"]  = 0
    counters["url"]   = 0
    counters["file"]  = 0
    counters["image"] = 0
    return {
        "message": "🗑️ All analyses deleted!",
        "deleted": counts
    }


# ══════════════════════════════════════════════════════════════
#  TEXT CRUD
# ══════════════════════════════════════════════════════════════

class TextRequest(BaseModel):
    text: str

class TextUpdateRequest(BaseModel):
    text: str
    note: Optional[str] = None


@app.post("/analyze/text", tags=["📝 Text CRUD"])
def create_text_analysis(req: TextRequest):
    """
    CREATE — Analyze new pasted article text.
    Sends text to Gemini AI and saves result.
    """
    if len(req.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text too short. Minimum 50 characters.")
    gemini_result = analyze_text(req.text)
    full_result = build_full_result(gemini_result, req.text)
    item_id = next_id("text")
    text_store[item_id] = {
        "id": item_id,
        "text_preview": req.text[:100] + "...",
        "full_text": req.text,
        "result": full_result,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    return {
        "message": "✅ Text analyzed and saved!",
        "id": item_id,
        "source": "text",
        "characters_analyzed": len(req.text),
        "result": full_result
    }


@app.get("/analyze/text", tags=["📝 Text CRUD"])
def get_all_text_analyses():
    """
    READ ALL — Get all saved text analyses.
    Returns all previously analyzed text articles.
    """
    return {
        "total": len(text_store),
        "analyses": list(text_store.values())
    }


@app.get("/analyze/text/{item_id}", tags=["📝 Text CRUD"])
def get_one_text_analysis(item_id: int):
    """
    READ ONE — Get one specific text analysis by ID.
    """
    if item_id not in text_store:
        raise HTTPException(status_code=404, detail=f"Text analysis {item_id} not found")
    return text_store[item_id]


@app.put("/analyze/text/{item_id}", tags=["📝 Text CRUD"])
def update_text_analysis(item_id: int, req: TextUpdateRequest):
    """
    UPDATE — Re-analyze text with new content or add a note.
    Re-runs Gemini AI on updated text and saves new result.
    """
    if item_id not in text_store:
        raise HTTPException(status_code=404, detail=f"Text analysis {item_id} not found")
    if len(req.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text too short. Minimum 50 characters.")
    gemini_result = analyze_text(req.text)
    full_result = build_full_result(gemini_result, req.text)
    text_store[item_id].update({
        "text_preview": req.text[:100] + "...",
        "full_text": req.text,
        "result": full_result,
        "note": req.note,
        "updated_at": datetime.now().isoformat()
    })
    return {
        "message": f"✅ Text analysis {item_id} updated!",
        "id": item_id,
        "result": full_result
    }


@app.delete("/analyze/text/{item_id}", tags=["📝 Text CRUD"])
def delete_text_analysis(item_id: int):
    """
    DELETE ONE — Delete one specific text analysis by ID.
    """
    if item_id not in text_store:
        raise HTTPException(status_code=404, detail=f"Text analysis {item_id} not found")
    del text_store[item_id]
    return {
        "message": f"🗑️ Text analysis {item_id} deleted!",
        "remaining": len(text_store)
    }


@app.delete("/analyze/text", tags=["📝 Text CRUD"])
def delete_all_text_analyses():
    """
    DELETE ALL — Delete all saved text analyses.
    """
    count = len(text_store)
    text_store.clear()
    return {
        "message": "🗑️ All text analyses deleted!",
        "deleted_count": count
    }


# ══════════════════════════════════════════════════════════════
#  URL CRUD
# ══════════════════════════════════════════════════════════════

class URLRequest(BaseModel):
    url: str

class URLUpdateRequest(BaseModel):
    url: str
    note: Optional[str] = None


@app.post("/analyze/url", tags=["🔗 URL CRUD"])
def create_url_analysis(req: URLRequest):
    """
    CREATE — Fetch and analyze a news article from URL.
    Auto-fetches article text then sends to Gemini AI.
    """
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http://")
    text, domain_credibility = extract_from_url(req.url)
    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text, source_override=domain_credibility)
    item_id = next_id("url")
    url_store[item_id] = {
        "id": item_id,
        "url": req.url,
        "domain_credibility": domain_credibility,
        "characters_analyzed": len(text),
        "result": full_result,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    return {
        "message": "✅ URL analyzed and saved!",
        "id": item_id,
        "source": "url",
        "url": req.url,
        "domain_credibility": domain_credibility,
        "result": full_result
    }


@app.get("/analyze/url", tags=["🔗 URL CRUD"])
def get_all_url_analyses():
    """
    READ ALL — Get all saved URL analyses.
    """
    return {
        "total": len(url_store),
        "analyses": list(url_store.values())
    }


@app.get("/analyze/url/{item_id}", tags=["🔗 URL CRUD"])
def get_one_url_analysis(item_id: int):
    """
    READ ONE — Get one specific URL analysis by ID.
    """
    if item_id not in url_store:
        raise HTTPException(status_code=404, detail=f"URL analysis {item_id} not found")
    return url_store[item_id]


@app.put("/analyze/url/{item_id}", tags=["🔗 URL CRUD"])
def update_url_analysis(item_id: int, req: URLUpdateRequest):
    """
    UPDATE — Re-analyze with a new URL or add a note.
    Re-fetches and re-analyzes the updated URL.
    """
    if item_id not in url_store:
        raise HTTPException(status_code=404, detail=f"URL analysis {item_id} not found")
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL.")
    text, domain_credibility = extract_from_url(req.url)
    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text, source_override=domain_credibility)
    url_store[item_id].update({
        "url": req.url,
        "domain_credibility": domain_credibility,
        "result": full_result,
        "note": req.note,
        "updated_at": datetime.now().isoformat()
    })
    return {
        "message": f"✅ URL analysis {item_id} updated!",
        "id": item_id,
        "result": full_result
    }


@app.delete("/analyze/url/{item_id}", tags=["🔗 URL CRUD"])
def delete_url_analysis(item_id: int):
    """
    DELETE ONE — Delete one specific URL analysis by ID.
    """
    if item_id not in url_store:
        raise HTTPException(status_code=404, detail=f"URL analysis {item_id} not found")
    del url_store[item_id]
    return {
        "message": f"🗑️ URL analysis {item_id} deleted!",
        "remaining": len(url_store)
    }


@app.delete("/analyze/url", tags=["🔗 URL CRUD"])
def delete_all_url_analyses():
    """
    DELETE ALL — Delete all saved URL analyses.
    """
    count = len(url_store)
    url_store.clear()
    return {
        "message": "🗑️ All URL analyses deleted!",
        "deleted_count": count
    }


# ══════════════════════════════════════════════════════════════
#  FILE CRUD
# ══════════════════════════════════════════════════════════════

@app.post("/analyze/file", tags=["📁 File CRUD"])
def create_file_analysis(file: UploadFile = File(...)):
    """
    CREATE — Upload and analyze a .txt or .pdf file.
    Extracts text from file then sends to Gemini AI.
    """
    filename = file.filename.lower()
    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files supported.")
    content = file.file.read()
    text = extract_pdf_text(content) if filename.endswith(".pdf") else content.decode("utf-8", errors="replace")
    text = text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="File content too short.")
    gemini_result = analyze_text(text)
    full_result = build_full_result(gemini_result, text)
    item_id = next_id("file")
    file_store[item_id] = {
        "id": item_id,
        "filename": file.filename,
        "characters_analyzed": len(text),
        "result": full_result,
        "created_at": datetime.now().isoformat()
    }
    return {
        "message": "✅ File analyzed and saved!",
        "id": item_id,
        "source": "file",
        "filename": file.filename,
        "characters_analyzed": len(text),
        "result": full_result
    }


@app.get("/analyze/file", tags=["📁 File CRUD"])
def get_all_file_analyses():
    """
    READ ALL — Get all saved file analyses.
    """
    return {
        "total": len(file_store),
        "analyses": list(file_store.values())
    }


@app.get("/analyze/file/{item_id}", tags=["📁 File CRUD"])
def get_one_file_analysis(item_id: int):
    """
    READ ONE — Get one specific file analysis by ID.
    """
    if item_id not in file_store:
        raise HTTPException(status_code=404, detail=f"File analysis {item_id} not found")
    return file_store[item_id]


@app.delete("/analyze/file/{item_id}", tags=["📁 File CRUD"])
def delete_file_analysis(item_id: int):
    """
    DELETE ONE — Delete one specific file analysis by ID.
    """
    if item_id not in file_store:
        raise HTTPException(status_code=404, detail=f"File analysis {item_id} not found")
    del file_store[item_id]
    return {
        "message": f"🗑️ File analysis {item_id} deleted!",
        "remaining": len(file_store)
    }


@app.delete("/analyze/file", tags=["📁 File CRUD"])
def delete_all_file_analyses():
    """
    DELETE ALL — Delete all saved file analyses.
    """
    count = len(file_store)
    file_store.clear()
    return {
        "message": "🗑️ All file analyses deleted!",
        "deleted_count": count
    }


# ══════════════════════════════════════════════════════════════
#  IMAGE CRUD
# ══════════════════════════════════════════════════════════════

@app.post("/analyze/image", tags=["🖼️ Image CRUD"])
def create_image_analysis(file: UploadFile = File(...)):
    """
    CREATE — Upload image to detect deepfakes or manipulation.
    Uses Gemini Vision AI for image analysis.
    """
    filename = file.filename.lower()
    allowed = [".jpg", ".jpeg", ".png", ".webp"]
    if not any(filename.endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Only .jpg .jpeg .png .webp supported.")
    content = file.file.read()
    mime = "image/png" if filename.endswith(".png") else "image/webp" if filename.endswith(".webp") else "image/jpeg"
    gemini_result = analyze_image(content, mime)
    item_id = next_id("image")
    image_store[item_id] = {
        "id": item_id,
        "filename": file.filename,
        "result": gemini_result,
        "created_at": datetime.now().isoformat()
    }
    return {
        "message": "✅ Image analyzed and saved!",
        "id": item_id,
        "source": "image",
        "filename": file.filename,
        "result": gemini_result
    }


@app.get("/analyze/image", tags=["🖼️ Image CRUD"])
def get_all_image_analyses():
    """
    READ ALL — Get all saved image analyses.
    """
    return {
        "total": len(image_store),
        "analyses": list(image_store.values())
    }


@app.get("/analyze/image/{item_id}", tags=["🖼️ Image CRUD"])
def get_one_image_analysis(item_id: int):
    """
    READ ONE — Get one specific image analysis by ID.
    """
    if item_id not in image_store:
        raise HTTPException(status_code=404, detail=f"Image analysis {item_id} not found")
    return image_store[item_id]


@app.delete("/analyze/image/{item_id}", tags=["🖼️ Image CRUD"])
def delete_image_analysis(item_id: int):
    """
    DELETE ONE — Delete one specific image analysis by ID.
    """
    if item_id not in image_store:
        raise HTTPException(status_code=404, detail=f"Image analysis {item_id} not found")
    del image_store[item_id]
    return {
        "message": f"🗑️ Image analysis {item_id} deleted!",
        "remaining": len(image_store)
    }


@app.delete("/analyze/image", tags=["🖼️ Image CRUD"])
def delete_all_image_analyses():
    """
    DELETE ALL — Delete all saved image analyses.
    """
    count = len(image_store)
    image_store.clear()
    return {
        "message": "🗑️ All image analyses deleted!",
        "deleted_count": count
    }