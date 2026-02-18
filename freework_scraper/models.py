"""Data models for FreeWork job postings."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FreeWorkJob:
    """Represents a single job posting extracted from free-work.com."""

    # --- Identity ---
    title: str = ""
    company_name: str = ""
    company_location: str = ""
    job_category: str = ""
    job_url: str = ""

    # --- Dates ---
    publish_date: str = ""
    start_date: str = ""

    # --- Contract details ---
    duration: str = ""
    experience: str = ""
    salary: str = ""
    remote: str = ""
    location: str = ""

    # --- Content ---
    description: str = ""
    skills: str = ""
    sector: str = ""

    # --- Meta ---
    scraped_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    search_url: str = ""
    page_number: int = 0
    status: str = "ok"
    error_message: str = ""

    def has_salary(self) -> bool:
        return bool(self.salary and self.salary.strip())

    def has_remote(self) -> bool:
        return bool(self.remote and self.remote.strip())

    def is_valid(self) -> bool:
        return bool(self.title and self.title.strip())

    def summary(self) -> str:
        parts = [self.title]
        if self.company_name:
            parts.append(f"@ {self.company_name}")
        if self.location:
            parts.append(f"({self.location})")
        return " ".join(parts)
