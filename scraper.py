"""
Coventry University Course Scraper
====================================
Scrapes structured data for 5 courses directly from https://www.coventry.ac.uk/
Source: Only official Coventry University webpages.

Author  : Senbonzakura Assignment Submission
Python  : 3.8+
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import logging
from typing import Optional

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
BASE_URL  = "https://www.coventry.ac.uk"
HEADERS   = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}
TARGET_COURSES           = 5
DELAY_BETWEEN_REQUESTS   = 2   # seconds – polite crawling

# Official Coventry University course page URLs
# Discovered from: https://www.coventry.ac.uk/search/?contentType=newcoursepage
SEED_COURSE_URLS = [
    "https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-mscibsc-hons/",
    "https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-with-artificial-intelligence-msci-bsc-hons/",
    "https://www.coventry.ac.uk/course-structure/pg/eec/cyber-security-msc/",
    "https://www.coventry.ac.uk/course-structure/pg/cbl/accounting-and-financial-management-msc/",
    "https://www.coventry.ac.uk/course-structure/ug/fbl/accounting-and-finance-bsc-hons/",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def get_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch a URL and return BeautifulSoup, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.exceptions.HTTPError as e:
        log.warning(f"HTTP error {e.response.status_code} for {url}")
    except requests.exceptions.ConnectionError:
        log.warning(f"Connection error for {url}")
    except requests.exceptions.Timeout:
        log.warning(f"Timeout for {url}")
    except Exception as exc:
        log.warning(f"Unexpected error fetching {url}: {exc}")
    return None


def clean(text: Optional[str]) -> str:
    """Normalise whitespace. Return 'NA' for empty/None."""
    if not text:
        return "NA"
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned if cleaned else "NA"


def find_text(soup: BeautifulSoup, *selectors) -> str:
    """Try CSS selectors in order; return first non-empty match."""
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            result = clean(tag.get_text())
            if result != "NA":
                return result
    return "NA"


def search_keyword(soup: BeautifulSoup, *keywords) -> str:
    """
    Search page for any tag whose text contains one of the keywords.
    Returns the first matching tag text (capped at 500 chars).
    Raw text is acceptable per assignment spec.
    """
    for kw in keywords:
        for tag in soup.find_all(["p", "li", "div", "span", "dd", "dt"]):
            txt = tag.get_text(" ", strip=True)
            if kw.lower() in txt.lower() and 8 < len(txt) < 600:
                return clean(txt)
    return "NA"


def extract_all_matching(soup: BeautifulSoup, keyword: str, cap: int = 400) -> str:
    """Collect all text snippets containing keyword, join with ' | '."""
    seen, results = set(), []
    for tag in soup.find_all(["p", "li", "div", "span"]):
        txt = tag.get_text(" ", strip=True)
        if keyword.lower() in txt.lower() and 8 < len(txt) < cap:
            c = clean(txt)
            if c not in seen:
                seen.add(c)
                results.append(c)
    return " | ".join(results[:5]) if results else "NA"


def extract_fees(soup: BeautifulSoup) -> str:
    """Extract tuition-fee information (raw text)."""
    # 1. Fees table rows
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells  = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            joined = " | ".join(cells)
            if any(k in joined.lower() for k in ["international", "fee", "tuition"]) and "£" in joined:
                return clean(joined[:400])
    # 2. Paragraph with pound sign
    for tag in soup.find_all(["p", "li", "div"]):
        txt = tag.get_text(" ", strip=True)
        if "£" in txt and ("fee" in txt.lower() or "tuition" in txt.lower()):
            return clean(txt[:400])
    return "NA"


def extract_duration(soup: BeautifulSoup) -> str:
    """Find duration text like '3 years full-time'."""
    for tag in soup.find_all(["p", "li", "div", "span", "dd"]):
        txt = tag.get_text(" ", strip=True)
        if re.search(r"\d\s*(year|years)", txt, re.I) and len(txt) < 150:
            return clean(txt)
    return "NA"


def extract_intakes(soup: BeautifulSoup) -> str:
    """Return all start-date text lines found on the page."""
    months  = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    pattern = re.compile(months + r"\s*\d{4}", re.I)
    seen, unique = set(), []
    for tag in soup.find_all(["p", "li", "div", "span", "a", "time"]):
        txt = tag.get_text(" ", strip=True)
        if pattern.search(txt) and len(txt) < 200:
            c = clean(txt)
            if c not in seen:
                seen.add(c)
                unique.append(c)
    return " | ".join(unique[:8]) if unique else "NA"


def extract_campus_and_level(url: str, soup: BeautifulSoup):
    """Infer campus and study level from URL path."""
    campus = "Coventry University, Coventry"
    if "/london/" in url or "/cul/" in url:
        campus = "Coventry University London"
    elif "/cuc/" in url:
        campus = "CU Coventry"
    elif "/cus/" in url:
        campus = "CU Scarborough"
    elif "/wroclaw/" in url:
        campus = "Coventry University Wrocław"

    level = "NA"
    if "/ug/" in url or "undergraduate" in url.lower():
        level = "Undergraduate"
    elif "/pg/" in url or any(s in url.lower() for s in ["-msc", "-ma-", "-mba", "postgraduate"]):
        level = "Postgraduate"

    return campus, level


# ──────────────────────────────────────────────────────────────
# CORE EXTRACTOR
# ──────────────────────────────────────────────────────────────

def extract_course_data(url: str) -> dict:
    """
    Scrape one Coventry University course page.
    All data sourced exclusively from coventry.ac.uk.
    """
    log.info(f"  Fetching → {url}")
    soup = get_page(url)

    if soup is None:
        log.warning(f"  Could not load page. Storing skeleton record.")
        return _skeleton(url)

    campus, study_level = extract_campus_and_level(url, soup)

    course_name        = find_text(soup, "h1.course-header__title", "h1.hero__title", "h1")
    yearly_tuition_fee = extract_fees(soup)
    course_duration    = extract_duration(soup)
    all_intakes        = extract_intakes(soup)

    # English requirements (raw text – as per assignment spec)
    min_ielts  = search_keyword(soup, "IELTS")
    min_pte    = search_keyword(soup, "PTE", "Pearson Test")
    min_toefl  = search_keyword(soup, "TOEFL")
    duolingo   = search_keyword(soup, "Duolingo")
    kaplan     = search_keyword(soup, "Kaplan")
    eng_waiver = search_keyword(soup, "english waiver", "waiver", "requirement waived")

    # Admission & entry requirements
    gre_gmat     = search_keyword(soup, "GRE", "GMAT")
    docs         = search_keyword(soup, "documents required", "required documents", "apply")
    scholarships = extract_all_matching(soup, "scholarship")
    ug_gpa       = search_keyword(soup, "GPA", "grade point")
    work_exp     = search_keyword(soup, "work experience", "professional experience")
    backlogs     = search_keyword(soup, "backlog", "outstanding debt")
    gap_year     = search_keyword(soup, "gap year", "gap in study")
    class12      = search_keyword(soup, "A Level", "A-Level", "12th", "class 12")

    return {
        "program_course_name":                   course_name,
        "university_name":                        "Coventry University",
        "course_website_url":                     url,
        "campus":                                 campus,
        "country":                                "United Kingdom",
        "address":                                "Priory Street, Coventry, CV1 5FB, UK",
        "study_level":                            study_level,
        "course_duration":                        course_duration,
        "all_intakes_available":                  all_intakes,
        "mandatory_documents_required":           docs,
        "yearly_tuition_fee":                     yearly_tuition_fee,
        "scholarship_availability":               scholarships,
        "gre_gmat_mandatory_min_score":           gre_gmat,
        "indian_regional_institution_restrictions": "NA",
        "class_12_boards_accepted":               class12,
        "gap_year_max_accepted":                  gap_year,
        "min_duolingo":                           duolingo,
        "english_waiver_class12":                 eng_waiver,
        "english_waiver_moi":                     eng_waiver,
        "min_ielts":                              min_ielts,
        "kaplan_test_of_english":                 kaplan,
        "min_pte":                                min_pte,
        "min_toefl":                              min_toefl,
        "ug_academic_min_gpa":                    ug_gpa,
        "twelfth_pass_min_cgpa":                  "NA",
        "mandatory_work_exp":                     work_exp,
        "max_backlogs":                           backlogs,
    }


def _skeleton(url: str) -> dict:
    """Placeholder record for pages that could not be loaded."""
    base = {k: "NA" for k in [
        "program_course_name", "university_name", "course_website_url", "campus",
        "country", "address", "study_level", "course_duration", "all_intakes_available",
        "mandatory_documents_required", "yearly_tuition_fee", "scholarship_availability",
        "gre_gmat_mandatory_min_score", "indian_regional_institution_restrictions",
        "class_12_boards_accepted", "gap_year_max_accepted", "min_duolingo",
        "english_waiver_class12", "english_waiver_moi", "min_ielts",
        "kaplan_test_of_english", "min_pte", "min_toefl", "ug_academic_min_gpa",
        "twelfth_pass_min_cgpa", "mandatory_work_exp", "max_backlogs",
    ]}
    base.update({
        "course_website_url": url,
        "university_name":    "Coventry University",
        "country":            "United Kingdom",
        "address":            "Priory Street, Coventry, CV1 5FB, UK",
    })
    return base


# ──────────────────────────────────────────────────────────────
# MAIN RUNNER
# ──────────────────────────────────────────────────────────────

def run_scraper(output_file: str = "coventry_courses.json") -> None:
    log.info("=" * 60)
    log.info("  Coventry University Course Scraper – Starting")
    log.info("=" * 60)

    results, seen_urls = [], set()

    for url in SEED_COURSE_URLS:
        if url in seen_urls:
            log.info(f"  Duplicate skipped: {url}")
            continue
        seen_urls.add(url)

        record = extract_course_data(url)
        results.append(record)
        log.info(f"  Saved: {record['program_course_name']}")

        if len(results) >= TARGET_COURSES:
            break

        time.sleep(DELAY_BETWEEN_REQUESTS)

    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    log.info("=" * 60)
    log.info(f"  Done. {len(results)} courses saved to '{output_file}'")
    log.info("=" * 60)


if __name__ == "__main__":
    run_scraper()