"""
Gemini AI Service — Core fake news detection using Google Gemini
Uses the NEW google-genai package (not deprecated)
"""

import os
import json
import re
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import HTTPException
from PIL import Image
import io

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env file!")

# ── New Gemini client ─────────────────────────────────────────
client = genai.Client(api_key=GEMINI_API_KEY)

# ── Models ────────────────────────────────────────────────────
MODEL_TEXT  = "gemini-2.5-flash"
MODEL_IMAGE = "gemini-2.5-flash"

# ── Text Analysis Prompt ──────────────────────────────────────
TEXT_PROMPT = """You are a world-class fact-checker and investigative journalist with 20+ years of experience detecting misinformation and fake news.

Analyze the news article below with deep scrutiny and determine if it is REAL or FAKE.

Check ALL of the following:
1. Language manipulation — sensational, fear-based, or emotionally charged words
2. Source credibility — are sources named, verifiable, and authoritative?
3. Factual consistency — do claims align with known facts?
4. Logical coherence — does the story make sense?
5. Headline accuracy — does headline match the article body?
6. Writing quality — professional journalism vs tabloid style
7. Conspiracy patterns — deep state, "they don't want you to know", suppression claims
8. Statistical claims — are numbers cited with proper context?
9. Dates and timeline — are events in correct chronological order?
10. Motive analysis — who benefits from spreading this story?

Respond ONLY with this exact JSON (no markdown, no extra text outside JSON):
{
  "verdict": "REAL" or "FAKE",
  "confidence": <integer 0-100>,
  "credibility_score": <integer 0-100>,
  "summary": "<2-3 clear sentences explaining your verdict>",
  "detailed_explanation": "<full paragraph with deep reasoning about why this is real or fake>",
  "reasons": [
    "<specific reason 1>",
    "<specific reason 2>",
    "<specific reason 3>",
    "<specific reason 4>"
  ],
  "red_flags": [
    "<specific red flag found in the article>",
    "<specific red flag found in the article>"
  ],
  "positive_signals": [
    "<credibility signal found>",
    "<credibility signal found>"
  ],
  "category": "<one of: Politics, Health, Science, Finance, Entertainment, Sports, Technology, Environment, Crime, Other>",
  "recommendation": "<specific advice for the reader about what to do with this information>"
}"""


# ── Image Analysis Prompt ─────────────────────────────────────
IMAGE_PROMPT = """You are an expert in detecting fake news images, manipulated photos, and AI-generated misinformation.

Analyze this image carefully and determine if it appears to be REAL (authentic) or FAKE (manipulated/misleading/AI-generated).

Examine:
1. Visual inconsistencies — lighting, shadows, edges, proportions
2. AI generation signs — uncanny faces, distorted hands, unnatural backgrounds
3. Manipulation signs — copy-paste artifacts, clone-stamping, unnatural blurs
4. Deepfake indicators — facial irregularities, unnatural expressions
5. Text in image — does any text look altered or out of place?

Respond ONLY with this exact JSON (no markdown, no extra text):
{
  "verdict": "REAL" or "FAKE",
  "confidence": <integer 0-100>,
  "credibility_score": <integer 0-100>,
  "summary": "<2-3 sentences describing what you see and your verdict>",
  "detailed_explanation": "<full paragraph explaining signs of manipulation or authenticity>",
  "reasons": ["<visual reason 1>", "<visual reason 2>", "<visual reason 3>"],
  "red_flags": ["<visual red flag>", "<visual red flag>"],
  "positive_signals": ["<authenticity signal>", "<authenticity signal>"],
  "category": "Image Analysis",
  "recommendation": "<what should the viewer do with this image>"
}"""


def parse_response(raw: str) -> dict:
    """Safely parse Gemini JSON response."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise HTTPException(
            status_code=500,
            detail="Gemini returned unexpected format. Please try again."
        )


def analyze_text(article_text: str) -> dict:
    """Analyze text article with Gemini."""
    try:
        prompt = f"{TEXT_PROMPT}\n\n--- ARTICLE START ---\n\n{article_text[:12000]}\n\n--- ARTICLE END ---"
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt
        )
        return parse_response(response.text)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="Gemini quota exceeded. Please wait a minute and try again."
            )
        if "404" in error_msg:
            raise HTTPException(
                status_code=404,
                detail="Gemini model not found. Please check model name."
            )
        raise HTTPException(status_code=500, detail=f"Gemini API error: {error_msg}")


def analyze_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Analyze image with Gemini Vision."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            image_bytes = buf.getvalue()
            mime_type = "image/jpeg"

        response = client.models.generate_content(
            model=MODEL_IMAGE,
            contents=[
                IMAGE_PROMPT,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            ]
        )
        return parse_response(response.text)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="Gemini quota exceeded. Please wait a minute and try again."
            )
        raise HTTPException(status_code=500, detail=f"Gemini Image API error: {error_msg}")