"""
Pydantic models for request and response schemas
"""

from pydantic import BaseModel
from typing import List, Optional


# ── Request Models ────────────────────────────────────────────

class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str


# ── Response Models ───────────────────────────────────────────

class AnalysisResult(BaseModel):
    verdict: str                        # "REAL" or "FAKE"
    confidence: int                     # 0-100
    credibility_score: int              # 0-100
    summary: str                        # 2-3 sentence explanation
    detailed_explanation: str           # full paragraph reasoning
    reasons: List[str]                  # why real or fake
    red_flags: List[str]                # warning signs
    positive_signals: List[str]         # credibility signs
    category: str                       # Politics, Health, etc.
    recommendation: str                 # what reader should do
    ml_score: Optional[float] = None    # ML heuristic score
    source_credibility: Optional[str] = None  # source trust level
    language_tone: Optional[str] = None       # Neutral / Biased / Sensational
    clickbait_score: Optional[int] = None     # 0-100


class AnalysisResponse(BaseModel):
    source: str
    result: AnalysisResult
    characters_analyzed: Optional[int] = None
    url: Optional[str] = None
    filename: Optional[str] = None
