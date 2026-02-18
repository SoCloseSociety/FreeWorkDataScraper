"""Search page navigation and pagination for FreeWork."""

from __future__ import annotations

import logging
import time
import random
from typing import Callable
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from bs4 import BeautifulSoup

from freework_scraper.config import (
    SELECTOR_PAGINATION_BTN,
    SELECTOR_SEARCH_RESULT,
    JOB_LINK_PREFIX,
    BASE_URL,
    PAGE_LOAD_WAIT,
    PAGE_LOAD_MAX,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)
from freework_scraper.scraper.browser import BrowserManager

logger = logging.getLogger(__name__)


def _random_delay(min_s: float = REQUEST_DELAY_MIN, max_s: float = REQUEST_DELAY_MAX) -> None:
    """Wait a random interval to mimic human behavior."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)


def _build_page_url(base_url: str, page: int) -> str:
    """Append or update the ?page= parameter on a URL."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    params["page"] = [str(page)]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def detect_total_pages(browser: BrowserManager) -> int:
    """Detect the total number of result pages from pagination buttons."""
    soup = BeautifulSoup(browser.page_source, "html.parser")
    page_numbers = []

    for btn in soup.select(SELECTOR_PAGINATION_BTN):
        data_page = btn.get("data-page")
        if data_page and data_page.isdigit():
            page_numbers.append(int(data_page))

    if not page_numbers:
        logger.warning("No pagination buttons found — assuming 1 page.")
        return 1

    total = max(page_numbers)
    logger.info("Detected %d total pages.", total)
    return total


def extract_job_links_from_page(browser: BrowserManager) -> list[str]:
    """Extract all job detail links from the current search results page."""
    soup = BeautifulSoup(browser.page_source, "html.parser")
    links: list[str] = []

    search_div = soup.find("div", attrs={"data-testid": "search-result"})
    if not search_div:
        logger.warning("Search result container not found on page.")
        return links

    seen = set()
    for a_tag in search_div.find_all("a", href=True):
        href = a_tag["href"]
        if JOB_LINK_PREFIX in href:
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in seen:
                seen.add(full_url)
                links.append(full_url)

    logger.info("Found %d job links on current page.", len(links))
    return links


def collect_all_job_links(
    browser: BrowserManager,
    search_url: str,
    max_pages: int = 0,
    on_page_done: Callable | None = None,
) -> list[str]:
    """
    Navigate through all search result pages and collect job links.

    Args:
        browser: Browser manager instance.
        search_url: The initial FreeWork search URL.
        max_pages: Max pages to scrape (0 = all).
        on_page_done: Optional callback(page_num, total_pages, links_count).

    Returns:
        List of all job detail URLs found.
    """
    # Load first page and detect pagination
    browser.get(search_url)
    time.sleep(random.uniform(PAGE_LOAD_WAIT, PAGE_LOAD_MAX))

    total_pages = detect_total_pages(browser)
    if max_pages > 0:
        total_pages = min(total_pages, max_pages)

    all_links: list[str] = []

    # Extract links from page 1 (already loaded)
    page_links = extract_job_links_from_page(browser)
    all_links.extend(page_links)
    if on_page_done:
        on_page_done(1, total_pages, len(page_links))

    # Continue from page 2 onwards
    for page_num in range(2, total_pages + 1):
        try:
            page_url = _build_page_url(search_url, page_num)
            logger.info("Loading page %d/%d: %s", page_num, total_pages, page_url)

            _random_delay()
            browser.get(page_url)
            time.sleep(random.uniform(PAGE_LOAD_WAIT, PAGE_LOAD_MAX))

            page_links = extract_job_links_from_page(browser)
            all_links.extend(page_links)

            if on_page_done:
                on_page_done(page_num, total_pages, len(page_links))

        except Exception as exc:
            logger.error("Error on page %d: %s", page_num, exc)
            if on_page_done:
                on_page_done(page_num, total_pages, 0)

    logger.info("Total job links collected: %d across %d pages.", len(all_links), total_pages)
    return all_links
