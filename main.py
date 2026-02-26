from __future__ import annotations

import argparse
import logging
import sys
import re

from freework_scraper import __version__
from freework_scraper.scraper.browser import BrowserManager
from freework_scraper.scraper.search import collect_all_job_links
from freework_scraper.scraper.job_extractor import extract_all_jobs
from freework_scraper.export.exporter import export_jobs

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("freework")

TRUSTED_DOMAIN = r"^https://www\.free-work\.com/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"FreeWork Data Scraper v{__version__} — Extract freelance jobs from free-work.com",
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        default="",
        help="FreeWork search URL (with filters applied).",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Output directory for exported files (default: output).",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["both", "excel", "csv"],
        default="both",
        help="Export format: both, excel, csv (default: both).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Max pages to scrape, 0 = all (default: 0).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run Chrome in headless mode (default: True).",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        default=False,
        help="Run Chrome with visible window.",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"FreeWork Data Scraper v{__version__}",
    )
    return parser.parse_args()


def validate_url(url: str) -> bool:
    return re.match(TRUSTED_DOMAIN, url) is not None


def main() -> None:
    args = parse_args()

    # Get search URL
    search_url = args.url
    if not search_url:
        search_url = input("Entrez l'URL de recherche FreeWork : ").strip()

    if not search_url or not validate_url(search_url):
        logger.error("URL invalide ou non fournie. Abandon.")
        sys.exit(1)

    headless = args.headless and not args.no_headless
    output_dir = args.output
    export_format = args.format
    max_pages = args.max_pages

    logger.info("=" * 60)
    logger.info("FreeWork Data Scraper v%s", __version__)
    logger.info("URL: %s", search_url)
    logger.info("Max pages: %s", max_pages if max_pages > 0 else "toutes")
    logger.info("Format: %s", export_format)
    logger.info("Headless: %s", headless)
    logger.info("=" * 60)

    browser = None
    try:
        # Start browser
        browser = BrowserManager(headless=headless)
        browser.start()

        # Collect job links
        logger.info("Phase 1: Collecte des liens de missions...")

        def on_page(page_num, total_pages, links_count):
            logger.info("  Page %d/%d — %d liens", page_num, total_pages, links_count)

        job_links = collect_all_job_links(
            browser,
            search_url,
            max_pages=max_pages,
            on_page_done=on_page,
        )

        if not job_links:
            logger.warning("Aucun lien de mission trouve. Verifiez l'URL.")
            sys.exit(0)

        logger.info("Total: %d liens de missions collectes.", len(job_links))

        # Extract job details
        logger.info("Phase 2: Extraction des details...")

        def on_job(idx, total, job):
            status = "OK" if job.status == "ok" else "ERR"
            logger.info("  [%d/%d] [%s] %s", idx, total, status, job.summary())

        jobs = extract_all_jobs(
            browser,
            job_links,
            search_url=search_url,
            on_job_done=on_job,
        )

        # Export
        logger.info("Phase 3: Export des donnees...")
        files = export_jobs(
            jobs,
            output_dir=output_dir,
            fmt=export_format,
            search_url=search_url,
        )

        # Summary
        ok = sum(1 for j in jobs if j.status == "ok")
        errors = sum(1 for j in jobs if j.status == "error")
        with_salary = sum(1 for j in jobs if j.has_salary())
        with_remote = sum(1 for j in jobs if j.has_remote())

        logger.info("=" * 60)
        logger.info("TERMINE !")
        logger.info("  Missions extraites : %d", ok)
        logger.info("  Erreurs            : %d", errors)
        logger.info("  Avec salaire/TJM   : %d", with_salary)
        logger.info("  Avec teletravail   : %d", with_remote)
        for f in files:
            logger.info("  Fichier : %s", f)
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("Interrompu par l'utilisateur.")
    except Exception as exc:
        logger.error("Erreur fatale: %s", exc, exc_info=True)
        sys.exit(1)
    finally:
        if browser:
            browser.quit()


if __name__ == "__main__":
    main()