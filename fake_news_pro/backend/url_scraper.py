"""
URL Scraper — Extracts clean article text from news URLs
"""

import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from fastapi import HTTPException


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Known trusted news domains for source credibility check
TRUSTED_DOMAINS = [
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com",
    "npr.org", "theguardian.com", "nytimes.com", "washingtonpost.com",
    "who.int", "nasa.gov", "cdc.gov", "nature.com", "economist.com",
    "bloomberg.com", "ft.com", "wsj.com", "time.com", "theatlantic.com",
    "scientificamerican.com", "newscientist.com"
]

UNTRUSTED_DOMAINS = [
    "infowars.com", "naturalnews.com", "beforeitsnews.com",
    "worldnewsdailyreport.com", "empirenews.net", "thedcgazette.com"
]


def check_domain_credibility(url: str) -> str:
    url_lower = url.lower()
    for domain in TRUSTED_DOMAINS:
        if domain in url_lower:
            return f"High — {domain} is a trusted source"
    for domain in UNTRUSTED_DOMAINS:
        if domain in url_lower:
            return f"Low — {domain} is known for misinformation"
    return "Medium — Source credibility unknown"


def extract_from_url(url: str) -> tuple[str, str]:
    """
    Returns: (article_text, domain_credibility)
    """
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"HTTP Error {e.code} when fetching URL")
    except urllib.error.URLError as e:
        raise HTTPException(status_code=400, detail=f"Could not reach URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(html, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "advertisement", "ads", "cookie", "popup"]):
        tag.decompose()

    # Try to get article body first
    article = soup.find("article")
    if article:
        text = article.get_text(separator="\n")
    else:
        text = soup.get_text(separator="\n")

    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    if len(clean_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract enough text from this URL. Try pasting the article text directly.")

    credibility = check_domain_credibility(url)
    return clean_text[:12000], credibility
