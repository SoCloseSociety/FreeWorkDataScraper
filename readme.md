<p align="center">
  <img src="assets/banner.svg" alt="FreeWork Data Scraper" width="900">
</p>

<p align="center">
  <strong>Extract freelance missions, salaries & contracts from free-work.com at scale — Streamlit UI & CLI.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-575ECF?style=flat-square" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10%2B-575ECF?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-575ECF?style=flat-square" alt="Platform">
  <a href="https://www.selenium.dev/"><img src="https://img.shields.io/badge/Selenium-4.20%2B-575ECF?style=flat-square&logo=selenium&logoColor=white" alt="Selenium"></a>
  <a href="https://github.com/SoCloseSociety/FreeWorkDataScraper/stargazers"><img src="https://img.shields.io/github/stars/SoCloseSociety/FreeWorkDataScraper?style=flat-square&color=575ECF" alt="GitHub Stars"></a>
  <a href="https://github.com/SoCloseSociety/FreeWorkDataScraper/issues"><img src="https://img.shields.io/github/issues/SoCloseSociety/FreeWorkDataScraper?style=flat-square&color=575ECF" alt="Issues"></a>
  <a href="https://github.com/SoCloseSociety/FreeWorkDataScraper/network/members"><img src="https://img.shields.io/github/forks/SoCloseSociety/FreeWorkDataScraper?style=flat-square&color=575ECF" alt="Forks"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#key-features">Features</a> &bull;
  <a href="#configuration">Configuration</a> &bull;
  <a href="#faq">FAQ</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

---

## What is FreeWork Data Scraper?

**FreeWork Data Scraper** is a free, open-source **freelance job scraper** built with Python and Selenium. It extracts job postings from [free-work.com](https://www.free-work.com/) at scale — collecting 18 data fields per job including title, company, salary/TJM, remote policy, duration, experience level, skills, and full descriptions.

The tool offers both a **Streamlit web dashboard** (recommended) with live progress and one-click downloads, and a **CLI** for scriptable automation. Output comes as professionally formatted Excel files or clean CSV.

### Who is this for?

- **Freelancers** monitoring the job market and tracking rates
- **Recruiters** building candidate pipelines and tracking demand
- **Data Analysts** studying freelance market trends and salary data
- **Startup Founders** researching talent availability and pricing
- **HR Departments** benchmarking contractor rates by skill
- **Developers** learning web scraping with Selenium and Streamlit

### Key Features

- **18 Data Fields** - Title, company, salary/TJM, remote policy, duration, experience, skills, description, and more
- **Streamlit Web UI** - Visual dashboard with live progress, metrics, and one-click downloads
- **CLI Mode** - Scriptable command-line interface with full argument support
- **Excel Export** - Color-coded headers, salary highlighting, clickable links, auto-filters, summary sheet
- **CSV Export** - UTF-8 encoded, ready for any data tool
- **Smart Pagination** - Automatically detects and navigates all result pages
- **SVG Icon Matching** - Identifies job attributes by matching SVG icon paths
- **Human-Like Behavior** - Random delays between requests to avoid detection
- **Cross-Platform** - Works on Windows, macOS (Intel & Apple Silicon), and Linux
- **Free & Open Source** - MIT license, no API key required

---

## Quick Start

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | Version 3.10 or higher ([Download](https://www.python.org/downloads/)) |
| **Google Chrome** | Latest version ([Download](https://www.google.com/chrome/)) |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SoCloseSociety/FreeWorkDataScraper.git
cd FreeWorkDataScraper

# 2. (Recommended) Create a virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Usage

#### Streamlit Web UI (recommended)

```bash
streamlit run app.py
```

This opens a dashboard in your browser where you can:
- Paste a FreeWork search URL
- Configure max pages, headless mode, and export format
- Watch live progress with real-time logs
- View results in an interactive table
- Download Excel and CSV files directly

#### Command Line

```bash
# Interactive mode — prompts for the URL
python main.py

# Direct URL mode
python main.py --url "https://www.free-work.com/fr/tech-it/jobs?query=python&contracts=contractor"

# With options
python main.py \
  --url "https://www.free-work.com/fr/tech-it/jobs?query=devops" \
  --max-pages 5 \
  --format excel \
  --output results \
  --no-headless
```

#### All CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--url, -u` | FreeWork search URL (with filters applied) | (interactive) |
| `--output, -o` | Output directory for exported files | `output` |
| `--format, -f` | Export format: `both`, `excel`, `csv` | `both` |
| `--max-pages` | Max pages to scrape (0 = all) | `0` |
| `--headless` | Run Chrome in headless mode | On |
| `--no-headless` | Run Chrome with visible window | Off |
| `--version, -v` | Show version and exit | — |

---

## How It Works

```
FreeWork Search URL
        │
        ▼
┌────────────────────────┐
│  1. Navigate to URL    │
│  2. Detect pagination  │
│  3. Collect job links  │
├────────────────────────┤
│  4. Visit each job     │
│  5. Parse 18 fields    │
│  6. SVG icon matching  │
├────────────────────────┤
│  7. Export Excel/CSV   │
│  8. Summary statistics │
└────────────────────────┘
```

---

## Extracted Data Fields

| Field | Description |
|-------|-------------|
| Title | Job posting title |
| Company | Company name |
| Company Location | Company city |
| Category | Job category (freelance, CDI, etc.) |
| Location | Mission location |
| Remote | Remote work policy |
| Salary / TJM | Daily rate or salary |
| Duration | Contract duration |
| Experience | Required experience level |
| Start Date | Mission start date |
| Publish Date | When the posting was published |
| Skills | Technologies and skills listed |
| Sector | Industry sector |
| Description | Full job description |
| Job URL | Link to the original posting |
| Page | Search result page number |
| Scraped At | Timestamp of extraction |
| Status | Extraction status (ok/error) |

---

## Excel Output

The Excel export includes:
- **Color-coded column headers** grouped by category (identity, details, contract, dates, skills, content, meta)
- **Salary highlighting** — green for jobs with salary info, red for missing
- **Remote highlighting** — purple tint for jobs with remote policy
- **Clickable URLs** — job links are hyperlinked
- **Auto-filters** on all columns
- **Frozen header row** and first column
- **Alternating row colors** for readability
- **Summary sheet** with statistics (total jobs, salary %, remote %, experience breakdown)

---

## Tech Stack

| Technology | Role |
|------------|------|
| [Python 3.10+](https://www.python.org/) | Core language |
| [Selenium 4.20+](https://www.selenium.dev/) | Browser automation |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing |
| [lxml](https://lxml.de/) | Fast HTML parser backend |
| [Pandas](https://pandas.pydata.org/) | Data manipulation & CSV export |
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel file creation & formatting |
| [Streamlit](https://streamlit.io/) | Web UI dashboard |
| [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) | Automatic ChromeDriver management |

---

## Project Structure

```
FreeWorkDataScraper/
├── main.py                              # CLI entry point
├── app.py                               # Streamlit web UI
├── requirements.txt                     # Python dependencies
├── freework_scraper/
│   ├── __init__.py                      # Package metadata (version, author)
│   ├── config.py                        # Constants, CSS selectors, SVG icon paths
│   ├── models.py                        # FreeWorkJob dataclass
│   ├── scraper/
│   │   ├── browser.py                   # Selenium Chrome browser manager
│   │   ├── search.py                    # Search page navigation & pagination
│   │   └── job_extractor.py             # Job detail page parser
│   └── export/
│       └── exporter.py                  # CSV & Excel export with formatting
├── assets/
│   └── banner.svg                       # Project banner
├── LICENSE                              # MIT License
├── README.md                            # This file
├── CONTRIBUTING.md                      # Contribution guidelines
└── .gitignore                           # Git ignore rules
```

---

## Troubleshooting

### Chrome driver issues

The scraper uses `webdriver-manager` to automatically download the correct ChromeDriver. If you encounter issues:

```bash
pip install --upgrade webdriver-manager
```

### No jobs found

If the scraper doesn't find any jobs:
1. Verify the FreeWork URL is valid and returns results in your browser
2. Try without `--headless` to see what's happening
3. FreeWork may have changed its HTML structure — open an issue

### Streamlit won't start

```bash
pip install --upgrade streamlit
streamlit run app.py
```

### Excel export fails

Make sure `openpyxl` is installed:

```bash
pip install openpyxl
```

---

## FAQ

**Q: Is this free?**
A: Yes. FreeWork Data Scraper is 100% free and open source under the MIT license.

**Q: Do I need an API key?**
A: No. This tool uses browser automation (Selenium), no API key needed.

**Q: How many jobs can I scrape?**
A: No hard limit. The scraper extracts all jobs from all pages of your search results. Use `--max-pages` to limit.

**Q: Can I export to Excel?**
A: Yes. The Excel export includes color-coded headers, salary highlighting, clickable links, and a summary statistics sheet.

**Q: Does it work on Mac / Linux?**
A: Yes. Fully cross-platform on Windows, macOS (Intel & Apple Silicon), and Linux.

**Q: Web UI or CLI?**
A: The Streamlit web UI is recommended for interactive use. The CLI is better for scripting and automation.

---

## Alternatives Comparison

| Feature | FreeWork Data Scraper | Manual Copy-Paste | Paid Job Scrapers |
|---------|----------------------|-------------------|--------------------|
| Price | **Free** | Free | $50-200/mo |
| 18 data fields | Yes | Manual | Varies |
| Excel with formatting | Yes | No | Basic |
| Open source | Yes | N/A | No |
| Web UI dashboard | Yes | N/A | Yes |
| API key required | No | No | Yes |
| Cross-platform | Yes | Yes | Web only |

---

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

This tool is provided for **educational and research purposes only**. Scraping free-work.com may be subject to their Terms of Service. The authors are not responsible for any misuse or consequences arising from the use of this software.

---

<p align="center">
  <strong>If this project helps you, please give it a star!</strong><br>
  It helps others discover this tool.<br><br>
  <a href="https://github.com/SoCloseSociety/FreeWorkDataScraper">
    <img src="https://img.shields.io/github/stars/SoCloseSociety/FreeWorkDataScraper?style=for-the-badge&logo=github&color=575ECF" alt="Star this repo">
  </a>
</p>

<br>

<p align="center">
  <sub>Built with purpose by <a href="https://soclose.co"><strong>SoClose</strong></a> &mdash; Digital Innovation Through Automation & AI</sub><br>
  <sub>
    <a href="https://soclose.co">Website</a> &bull;
    <a href="https://linkedin.com/company/soclose-agency">LinkedIn</a> &bull;
    <a href="https://twitter.com/SoCloseAgency">Twitter</a> &bull;
    <a href="mailto:hello@soclose.co">Contact</a>
  </sub>
</p>
