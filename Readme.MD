# Coventry University Course Scraper

**Author:** Shubham Singh Mewada.  
**Email:** shubhamsinghmewada3@gmail.com. 
**Submission:** Senbonzakura Consultancy Private Limited – Intern Assignment.  
**Date:** April 2026  

---

Scrapes structured data for **5 courses** directly from the official Coventry University website:  
🔗 https://www.coventry.ac.uk/

> All data is sourced **only** from official `coventry.ac.uk` pages.  
> No third-party platforms, pre-existing datasets, or manual copy-pasting are used.

---

## Project Structure

```
coventry_scraper/
├── scraper.py            ← Main scraper (run this)
├── coventry_courses.json ← Output file (auto-generated)
└── README.md             ← This file
```

---

## Dependencies

| Package        | Purpose                          |
|----------------|----------------------------------|
| `requests`     | HTTP requests to coventry.ac.uk  |
| `beautifulsoup4` | HTML parsing                   |
| `lxml`         | Fast HTML parser backend         |

All are available on PyPI.

---

## Setup Steps

### 1. Make sure Python 3.8+ is installed
```bash
python --version
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install requests beautifulsoup4 lxml
```

---

## How to Run

```bash
python scraper.py
```

The scraper will:
1. Visit 5 Coventry University course pages (hardcoded official URLs)
2. Extract all required fields from each page
3. Save the output to `coventry_courses.json`

You will see progress logs like this:
```
2026-04-13 15:25:32,564 [INFO] ============================================================
2026-04-13 15:25:32,564 [INFO]   Coventry University Course Scraper – Starting
2026-04-13 15:25:32,568 [INFO] ============================================================
2026-04-13 15:25:32,568 [INFO]   Fetching → https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-mscibsc-hons/
2026-04-13 15:25:34,373 [INFO]   Saved: Computer Science MSci/BSc (Hons)
2026-04-13 15:25:36,373 [INFO]   Fetching → https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-with-artificial-intelligence-msci-bsc-hons/
2026-04-13 15:25:37,661 [INFO]   Saved: Computer Science with Artificial Intelligence MSci/BSc (Hons)
2026-04-13 15:25:39,661 [INFO]   Fetching → https://www.coventry.ac.uk/course-structure/pg/eec/cyber-security-msc/
2026-04-13 15:25:41,132 [INFO]   Saved: Cyber Security MSc
2026-04-13 15:25:43,132 [INFO]   Fetching → https://www.coventry.ac.uk/course-structure/pg/cbl/accounting-and-financial-management-msc/
2026-04-13 15:25:44,302 [INFO]   Saved: Accounting and Financial Management MSc
2026-04-13 15:25:46,302 [INFO]   Fetching → https://www.coventry.ac.uk/course-structure/ug/fbl/accounting-and-finance-bsc-hons/
2026-04-13 15:25:47,698 [INFO]   Saved: Accounting and Finance BSc (Hons)
2026-04-13 15:25:47,699 [INFO] ============================================================
2026-04-13 15:25:47,699 [INFO]   Done. 5 courses saved to 'coventry_courses.json'
2026-04-13 15:25:47,699 [INFO] ============================================================
```

### ✅ Successful Run Screenshot

The screenshot below shows a successful end-to-end run with all 5 courses scraped and saved:

![Scraper Output](scraper_output.png)

All 5 courses were fetched and saved to `coventry_courses.json` in approximately 15 seconds.

---

## Scraped Course URLs (Official Source)

| # | Course | URL |
|---|--------|-----|
| 1 | MSci/BSc (Hons) Computer Science | https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-mscibsc-hons/ |
| 2 | BSc (Hons) Computer Science with AI | https://www.coventry.ac.uk/course-structure/ug/eec/computer-science-with-artificial-intelligence-msci-bsc-hons/ |
| 3 | Cyber Security MSc | https://www.coventry.ac.uk/course-structure/pg/eec/cyber-security-msc/ |
| 4 | Accounting and Financial Management MSc | https://www.coventry.ac.uk/course-structure/pg/cbl/accounting-and-financial-management-msc/ |
| 5 | Accounting and Finance BSc (Hons) | https://www.coventry.ac.uk/course-structure/ug/fbl/accounting-and-finance-bsc-hons/ |

---

## Output Format Explanation

The output is a **JSON array** with exactly **5 objects** – one per course.

Each object follows this schema:

| Field | Description |
|-------|-------------|
| `program_course_name` | Full course title as shown on the page |
| `university_name` | Always "Coventry University" |
| `course_website_url` | The exact official course page URL |
| `campus` | Inferred from URL and page (e.g., Coventry, London, Scarborough) |
| `country` | Always "United Kingdom" |
| `address` | University postal address |
| `study_level` | "Undergraduate" or "Postgraduate" |
| `course_duration` | Duration text extracted from the page |
| `all_intakes_available` | Start dates found on the page, separated by `\|` |
| `mandatory_documents_required` | Application/document text from the page |
| `yearly_tuition_fee` | Fee text from the page (raw, with £ symbol) |
| `scholarship_availability` | Scholarship text extracted from the page |
| `gre_gmat_mandatory_min_score` | GRE/GMAT requirement (usually "NA" for UK) |
| `indian_regional_institution_restrictions` | "NA" (not specified on site) |
| `class_12_boards_accepted` | A Level / BTEC / IB acceptance text |
| `gap_year_max_accepted` | Gap year policy text if available |
| `min_duolingo` | Duolingo score requirement if stated |
| `english_waiver_class12` | English waiver info from the page |
| `english_waiver_moi` | MOI (Medium of Instruction) waiver info |
| `min_ielts` | IELTS requirement text extracted from the page |
| `kaplan_test_of_english` | Kaplan requirement if stated |
| `min_pte` | PTE requirement text if stated |
| `min_toefl` | TOEFL requirement text if stated |
| `ug_academic_min_gpa` | Minimum GPA requirement if stated |
| `twelfth_pass_min_cgpa` | "NA" (not specified on site) |
| `mandatory_work_exp` | Work experience info from the page |
| `max_backlogs` | Backlog policy if stated |

> Fields not found on the page return `"NA"`.  
> Raw text is used as-is (per assignment spec — no over-engineering of parsing).

---

## Design Decisions

- **Polite crawling**: 2-second delay between requests  
- **Modular functions**: Each extraction concern (fees, IELTS, duration, etc.) is its own function  
- **Graceful missing values**: All `"NA"` returns handled centrally in `clean()`  
- **Duplicate prevention**: `seen_urls` set prevents re-scraping  
- **Error handling**: `get_page()` catches HTTP errors, timeouts, and connection errors without crashing  
- **Raw text extraction**: Assignment explicitly allows raw text — no over-engineered regex normalisation  

---

## Notes

- The scraper runs end-to-end without any manual intervention  
- If a page fails to load, a skeleton record is stored (all fields = `"NA"`, URL preserved)  
- Course URLs were discovered from: `https://www.coventry.ac.uk/search/?contentType=newcoursepage`
