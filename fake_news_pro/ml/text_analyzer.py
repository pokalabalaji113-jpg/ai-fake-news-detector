"""
ML Text Analyzer — Heuristic scoring using NLP signals
Adds extra confidence layer on top of Gemini AI
"""

import re
import math
from typing import Tuple


# ── Fake news signal word lists ───────────────────────────────

SENSATIONAL_WORDS = [
    "breaking", "shocking", "bombshell", "explosive", "secret",
    "exposed", "banned", "censored", "suppressed", "leaked",
    "they don't want you to know", "share before deleted",
    "mainstream media won't tell", "deep state", "illuminati",
    "wake up", "urgent", "alert", "miracle", "cure", "instant",
    "doctors hate", "big pharma", "government hiding", "proof",
    "100%", "guaranteed", "you won't believe", "mind blowing",
    "hoax", "scam", "fake", "lie", "cover up", "conspiracy"
]

CREDIBLE_SIGNALS = [
    "according to", "research shows", "study finds", "experts say",
    "officials said", "confirmed by", "data shows", "report says",
    "spokesperson", "statement", "published in", "journal",
    "university", "institute", "department", "agency", "percent",
    "statistics", "evidence", "source", "cited", "quoted"
]

EMOTIONAL_PATTERNS = [
    r'\b(must|need to|have to)\s+share\b',
    r'\bshare\s+(this|before|now|immediately)\b',
    r'\b(wake\s+up|open\s+your\s+eyes)\b',
    r'\b(they|government|elite)\s+(are|is)\s+(hiding|lying|suppressing)\b',
    r'!!!+',
    r'\?{2,}',
    r'[A-Z]{4,}',   # lots of caps like BREAKING ALERT
]

CLICKBAIT_PATTERNS = [
    r"you won't believe",
    r"what happens next",
    r"this one (trick|secret|tip)",
    r"doctors (hate|don't want)",
    r"number \d+ will shock you",
    r"before it('s| is) (deleted|removed|banned)",
    r"share (this|before|now)",
]


def count_caps_ratio(text: str) -> float:
    """How much of the text is in CAPS (signal of sensationalism)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    caps = [c for c in letters if c.isupper()]
    return len(caps) / len(letters)


def count_exclamations(text: str) -> int:
    return text.count("!")


def count_question_marks(text: str) -> int:
    return text.count("?")


def get_avg_sentence_length(text: str) -> float:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0
    return sum(len(s.split()) for s in sentences) / len(sentences)


def ml_analyze(text: str) -> Tuple[float, str, int, str]:
    """
    Returns:
        ml_score (float 0-1, higher = more likely fake)
        language_tone (str)
        clickbait_score (int 0-100)
        source_credibility (str)
    """
    text_lower = text.lower()
    score = 0.0
    max_score = 0.0

    # ── Sensational words ──
    sensational_hits = sum(1 for w in SENSATIONAL_WORDS if w in text_lower)
    score += min(sensational_hits * 0.05, 0.30)
    max_score += 0.30

    # ── Credible signals ──
    credible_hits = sum(1 for w in CREDIBLE_SIGNALS if w in text_lower)
    score -= min(credible_hits * 0.03, 0.20)
    max_score += 0.20

    # ── Emotional manipulation patterns ──
    emotional_hits = sum(1 for p in EMOTIONAL_PATTERNS if re.search(p, text_lower))
    score += min(emotional_hits * 0.08, 0.24)
    max_score += 0.24

    # ── Caps ratio ──
    caps = count_caps_ratio(text)
    if caps > 0.3:
        score += 0.15
    elif caps > 0.15:
        score += 0.07

    # ── Exclamations ──
    excl = count_exclamations(text)
    score += min(excl * 0.02, 0.10)

    # ── Short sentences (tabloid style) ──
    avg_len = get_avg_sentence_length(text)
    if avg_len < 8:
        score += 0.05

    # ── Clickbait score ──
    clickbait_hits = sum(1 for p in CLICKBAIT_PATTERNS if re.search(p, text_lower))
    clickbait_score = min(clickbait_hits * 25, 100)

    # ── Normalize ml_score to 0-1 ──
    ml_score = max(0.0, min(1.0, score))

    # ── Language tone ──
    if caps > 0.25 or excl > 5 or emotional_hits >= 2:
        language_tone = "Sensational"
    elif sensational_hits > 3 or clickbait_hits > 0:
        language_tone = "Biased"
    elif credible_hits >= 3:
        language_tone = "Neutral / Professional"
    else:
        language_tone = "Neutral"

    # ── Source credibility ──
    trusted_domains = [
        "bbc", "reuters", "apnews", "npr", "theguardian",
        "nytimes", "washingtonpost", "who.int", "nasa.gov",
        "cdc.gov", "nature.com", "science.org", "economist"
    ]
    untrusted_signals = [
        "blog", "wordpress", "wix", "tumblr", "freewebs",
        "infowars", "naturalnews", "beforeitsnews"
    ]

    source_credibility = "Unknown"
    for domain in trusted_domains:
        if domain in text_lower:
            source_credibility = "High — Trusted Source"
            break
    for signal in untrusted_signals:
        if signal in text_lower:
            source_credibility = "Low — Unreliable Source"
            break

    return round(ml_score, 3), language_tone, clickbait_score, source_credibility
