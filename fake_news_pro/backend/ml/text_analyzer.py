"""
ml/text_analyzer.py
ML heuristic analysis — extra signals on top of Gemini AI.
Uses rule-based NLP patterns, keyword scoring, and statistical features.
No heavy model downloads needed — works out of the box.
"""

import re
from typing import Dict


# ── Fake news keyword patterns ────────────────────────────────────────────────

FAKE_KEYWORDS = [
    # Urgency / panic
    "breaking", "urgent", "alert", "shocking", "bombshell", "explosive",
    "must read", "share before deleted", "share now", "before it's too late",
    # Conspiracy
    "deep state", "new world order", "illuminati", "they don't want you to know",
    "mainstream media won't tell", "suppressed", "cover up", "coverup",
    "secret cure", "miracle cure", "doctors hate", "big pharma",
    # Clickbait
    "you won't believe", "what happened next", "this will shock you",
    "mind blowing", "jaw dropping", "incredible secret",
    # Fake authority
    "scientists say", "experts reveal", "insiders confirm", "whistleblower",
    "anonymous source", "insider source",
    # Extreme language
    "completely destroy", "obliterate", "annihilate", "evil agenda",
    "wake up sheeple", "sheeple", "censored", "banned",
]

CREDIBLE_SIGNALS = [
    # Named sources
    "according to", "stated that", "confirmed by", "announced",
    "reported by", "spokesperson", "official", "government", "ministry",
    # Research
    "study", "research", "published in", "peer reviewed", "journal",
    "university", "institute", "data shows", "statistics",
    # Balanced language
    "however", "on the other hand", "critics say", "supporters argue",
    "experts disagree", "further investigation",
    # Attribution
    "said in a statement", "told reporters", "press conference",
    "cited sources", "based on data",
]

EMOTIONAL_WORDS = [
    "outrage", "disgusting", "horrifying", "terrifying", "devastating",
    "shocking", "unbelievable", "incredible", "amazing", "explosive",
    "scandal", "corruption", "betrayal", "lies", "hoax", "fake", "fraud",
]

CAPS_PATTERN = re.compile(r'\b[A-Z]{3,}\b')
EXCLAMATION_PATTERN = re.compile(r'!')
URL_PATTERN = re.compile(r'http[s]?://\S+')
NUMBER_PATTERN = re.compile(r'\b\d+%|\b\d+\s*(people|cases|deaths|victims)\b', re.IGNORECASE)


def analyze_text_ml(text: str) -> Dict:
    """
    Run ML heuristic analysis on article text.
    Returns scores and signals.
    """
    text_lower = text.lower()
    words = text_lower.split()
    total_words = max(len(words), 1)

    # ── Fake keyword score ────────────────────────────────────────────────────
    fake_hits = [kw for kw in FAKE_KEYWORDS if kw in text_lower]
    fake_keyword_score = min(len(fake_hits) * 8, 80)

    # ── Credibility score ─────────────────────────────────────────────────────
    credible_hits = [kw for kw in CREDIBLE_SIGNALS if kw in text_lower]
    credible_score = min(len(credible_hits) * 6, 60)

    # ── Emotional language score ──────────────────────────────────────────────
    emotional_hits = [w for w in EMOTIONAL_WORDS if w in text_lower]
    emotional_score = min(len(emotional_hits) * 5, 50)

    # ── CAPS abuse ────────────────────────────────────────────────────────────
    caps_words = CAPS_PATTERN.findall(text)
    caps_ratio = len(caps_words) / total_words
    caps_score = min(int(caps_ratio * 500), 40)

    # ── Exclamation abuse ─────────────────────────────────────────────────────
    exclamations = len(EXCLAMATION_PATTERN.findall(text))
    exclamation_score = min(exclamations * 4, 30)

    # ── Statistical claims (credibility signal) ───────────────────────────────
    has_numbers = bool(NUMBER_PATTERN.search(text))

    # ── Text length (very short = suspicious) ────────────────────────────────
    length_penalty = 20 if total_words < 50 else 10 if total_words < 100 else 0

    # ── Clickbait detection ───────────────────────────────────────────────────
    clickbait_phrases = [
        "you won't believe", "what happens next", "this is why",
        "the real truth", "they lied", "nobody is talking about"
    ]
    clickbait_hits = sum(1 for p in clickbait_phrases if p in text_lower)
    clickbait_score = min(clickbait_hits * 20, 100)

    # ── Sentiment ─────────────────────────────────────────────────────────────
    positive_words = ["good", "great", "positive", "success", "improve", "benefit", "safe"]
    negative_words = ["bad", "terrible", "dangerous", "threat", "crisis", "attack", "fail"]
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    if neg_count > pos_count * 2:
        sentiment = "Highly Negative"
    elif neg_count > pos_count:
        sentiment = "Negative"
    elif pos_count > neg_count:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    # ── Bias detection ────────────────────────────────────────────────────────
    bias_words = ["always", "never", "everyone", "nobody", "all", "none", "every", "only"]
    bias_hits = sum(1 for w in bias_words if w in text_lower)
    if bias_hits > 5:
        bias_level = "High Bias"
    elif bias_hits > 2:
        bias_level = "Moderate Bias"
    else:
        bias_level = "Low Bias"

    # ── Final ML fake score (0-100, higher = more likely fake) ───────────────
    raw_fake_score = (
        fake_keyword_score * 0.35 +
        emotional_score * 0.20 +
        caps_score * 0.15 +
        exclamation_score * 0.10 +
        length_penalty * 0.10 +
        clickbait_score * 0.10
    ) - (credible_score * 0.3) - (10 if has_numbers else 0)

    ml_fake_score = max(0, min(100, int(raw_fake_score)))
    ml_real_score = 100 - ml_fake_score

    return {
        "ml_fake_score": ml_fake_score,
        "ml_real_score": ml_real_score,
        "ml_verdict": "FAKE" if ml_fake_score > 50 else "REAL",
        "clickbait_score": clickbait_score,
        "sentiment": sentiment,
        "bias_level": bias_level,
        "fake_keywords_found": fake_hits[:5],
        "credible_signals_found": credible_hits[:5],
        "caps_abuse": caps_ratio > 0.05,
        "exclamation_abuse": exclamations > 3,
        "has_statistics": has_numbers,
        "word_count": total_words,
    }


def get_source_credibility(url: str) -> Dict:
    """
    Check if URL domain is from a known credible or fake news source.
    """
    CREDIBLE_DOMAINS = [
        "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "bloomberg.com",
        "nytimes.com", "theguardian.com", "washingtonpost.com", "economist.com",
        "nature.com", "science.org", "who.int", "nasa.gov", "cdc.gov",
        "npr.org", "pbs.org", "time.com", "forbes.com", "ft.com",
        "wsj.com", "theatlantic.com", "newyorker.com", "politico.com",
        "ndtv.com", "thehindu.com", "indianexpress.com", "hindustantimes.com",
    ]
    FAKE_DOMAINS = [
        "worldnewsdailyreport", "empirenews", "huzlers", "nationalreport",
        "theonion", "clickhole", "babylonbee", "thespoof", "newsbiscuit",
        "waterfordwhispersnews", "reductress",
    ]

    domain = url.lower()

    for d in CREDIBLE_DOMAINS:
        if d in domain:
            return {"rating": "Highly Credible", "score": 90, "color": "green"}

    for d in FAKE_DOMAINS:
        if d in domain:
            return {"rating": "Known Satire/Fake", "score": 5, "color": "red"}

    return {"rating": "Unknown Source", "score": 50, "color": "orange"}
