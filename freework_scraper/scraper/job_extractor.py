from __future__ import annotations

import logging
import re
time
import random
from datetime import datetime
from typing import Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup

from freework_scraper.config import (
    SVG_ICON_PATHS,
    SELECTOR_JOB_HEADER,
    SELECTOR_JOB_TIME,
    SELECTOR_JOB_CONTENT,
    SELECTOR_ICON_CONTAINER,
    SELECTOR_ICON_TEXT,
    PAGE_LOAD_WAIT,
    PAGE_LOAD_MAX,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)
from freework_scraper.models import FreeWorkJob
from freework_scraper.scraper.browser import BrowserManager

logger = logging.getLogger(__name__)

def _match_icon(svg_d: str) -> str | None:
    """Match an SVG path 'd' attribute to a known icon type."""
    if not svg_d:
        return None
    cleaned = svg_d.strip()
    for icon_name, icon_path in SVG_ICON_PATHS.items():
        if cleaned == icon_path:
            return icon_name
    return None

def _clean_text(text: str | None) -> str:
    """Clean extracted text: strip whitespace and normalize spaces."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned

def _extract_header(soup: BeautifulSoup) -> dict[str, str]:
    """Extract header information (title, company, location, category)."""
    result = {"title": "", "company_name": "", "company_location": "", "job_category": ""}

    header_div = soup.find("div", class_=lambda c: c and "text-white" in c and "w-full" in c)
    if not header_div:
        header_div = soup.select_one(SELECTOR_JOB_HEADER)

    if not header_div:
        logger.warning("Job header not found.")
        return result

    text = header_div.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    fields = ["title", "company_name", "company_location", "job_category"]
    for i, field in enumerate(fields):
        if i < len(lines):
            result[field] = lines[i]

    return result

def _extract_publish_date(soup: BeautifulSoup) -> str:
    """Extract job publish date."""
    time_tag = soup.find("time", class_=lambda c: c and "text-sm" in c)
    if not time_tag:
        time_tag = soup.select_one(SELECTOR_JOB_TIME)
    return _clean_text(time_tag.text) if time_tag else ""

def _extract_description(soup: BeautifulSoup) -> str:
    """Extract full job description content."""
    content_div = soup.find("div", class_="prose-content")
    if not content_div:
        content_div = soup.select_one(SELECTOR_JOB_CONTENT)

    if not content_div:
        return ""

    # Get text with paragraph separation
    paragraphs = content_div.get_text(separator="\n").split("\n")
    cleaned = [line.strip() for line in paragraphs if line.strip()]
    return "\n".join(cleaned)

def _extract_icon_attributes(soup: BeautifulSoup) -> dict[str, str]:
    """Extract job attributes from SVG icon containers."""
    attributes = {
        "calendar": "",
        "duration": "",
        "experience": "",
        "location": "",
        "salary": "",
        "remote": "",
    }

    containers = soup.find_all("div", class_=lambda c: c and "flex" in c and "items-center" in c and "py-1" in c)
    if not containers:
        containers = soup.select(SELECTOR_ICON_CONTAINER)

    for container in containers:
        path_el = container.find("path", attrs={"d": True})
        if not path_el:
            continue

        icon_type = _match_icon(path_el["d"])
        if not icon_type:
            continue

        span = container.find("span", class_=lambda c: c and "text-sm" in c)
        if not span:
            span = container.select_one(SELECTOR_ICON_TEXT)

        if span:
            attributes[icon_type] = _clean_text(span.text)

    return attributes

def _extract_skills(soup: BeautifulSoup) -> str:
    """Extract skills/technologies from the job page."""
    skills = []

    # Look for skill tags/badges
    skill_containers = soup.find_all("span", class_=lambda c: c and "badge" in str(c).lower())
    for badge in skill_containers:
        text = _clean_text(badge.text)
        if text and len(text) < 50:
            skills.append(text)

    # Look for technology tags
    tech_divs = soup.find_all("a", class_=lambda c: c and "tag" in str(c).lower())
    for tag in tech_divs:
        text = _clean_text(tag.text)
        if text and len(text) < 50 and text not in skills:
            skills.append(text)

    return ", ".join(skills)

def _extract_sector(soup: BeautifulSoup) -> str:
    """Extract job sector/industry if available."""
    # Look for breadcrumbs or category links
    breadcrumbs = soup.find("nav", attrs={"aria-label": "breadcrumb"})
    if breadcrumbs:
        items = breadcrumbs.find_all("a")
        if len(items) >= 2:
            return _clean_text(items[-1].text)

    return ""

def extract_job_detail(browser: BrowserManager, job_url: str, search_url: str = "", page_num: int = 0) -> FreeWorkJob:
    """Navigate to a job detail page and extract all available data.

    Args:
        browser: Browser manager instance.
        job_url: Full URL to the job detail page.
        search_url: Original search URL for metadata.
        page_num: Page number where this job was found.

    Returns:
        FreeWorkJob instance with extracted data.
    """
    job = FreeWorkJob(
        job_url=job_url,
        search_url=search_url,
        page_number=page_num,
        scraped_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    try:
        browser.get(job_url)
        time.sleep(random.uniform(PAGE_LOAD_WAIT, PAGE_LOAD_MAX))

        soup = BeautifulSoup(browser.page_source, "html.parser")

        # Header info
        header = _extract_header(soup)
        job.title = header["title"]
        job.company_name = header["company_name"]
        job.company_location = header["company_location"]
        job.job_category = header["job_category"]

        # Publish date
        job.publish_date = _extract_publish_date(soup)

        # Description
        job.description = _extract_description(soup)

        # Icon-based attributes
        attrs = _extract_icon_attributes(soup)
        job.start_date = attrs.get("calendar", "")
        job.duration = attrs.get("duration", "")
        job.experience = attrs.get("experience", "")
        job.location = attrs.get("location", "")
        job.salary = attrs.get("salary", "")
        job.remote = attrs.get("remote", "")

        # Skills
        job.skills = _extract_skills(soup)

        # Sector
        job.sector = _extract_sector(soup)

        job.status = "ok"
        logger.info("Extracted: %s", job.summary())

    except Exception as exc:
        job.status = "error"
        job.error_message = str(exc)
        logger.error("Error extracting %s: %s", job_url, exc)

    return job

def extract_all_jobs(
    browser: BrowserManager,
    job_links: List[str],
    search_url: str = "",
    on_job_done: Callable | None = None,
) -> List[FreeWorkJob]:
    """Extract details for all job links.

    Args:
        browser: Browser manager instance.
        job_links: List of job detail URLs.
        search_url: Original search URL for metadata.
        on_job_done: Optional callback(index, total, job).

    Returns:
        List of FreeWorkJob instances.
    """
    jobs: List[FreeWorkJob] = []
    total = len(job_links)

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(extract_job_detail, browser, url, search_url=search_url): url for url in job_links}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                job = future.result()
                jobs.append(job)

                if on_job_done:
                    idx = job_links.index(url) + 1
                    on_job_done(idx, total, job)

            except Exception as exc:
                logger.error("Error extracting %s: %s", url, exc)
                job = FreeWorkJob(
                    job_url=url,
                    search_url=search_url,
                    status="error",
                    error_message=str(exc),
                )
                jobs.append(job)

            # Delay between requests
            time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    valid = sum(1 for j in jobs if j.status == "ok")
    errors = sum(1 for j in jobs if j.status == "error")
    logger.info("Extraction complete: %d valid, %d errors out of %d total.", valid, errors, total)

    return jobs