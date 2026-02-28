from __future__ import annotations

import logging
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from freework_scraper.config import USER_AGENT

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages Selenium Chrome browser lifecycle — Windows, Mac & Linux."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver: webdriver.Chrome | None = None

    def start(self) -> webdriver.Chrome:
        """Start Chrome browser with optimal settings."""
        options = self._build_options()
        service = Service(ChromeDriverManager().install())

        logger.info("Launching Chrome (headless=%s) on %s...", self.headless, platform.system())
        self.driver = webdriver.Chrome(service=service, options=options)

        if not self.headless:
            self.driver.maximize_window()

        logger.info("Browser started successfully.")
        return self.driver

    def _build_options(self) -> Options:
        """Build Chrome options for cross-platform compatibility."""
        options = Options()

        # Core stability flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument(f"--user-agent={USER_AGENT}")
        options.add_argument("--window-size=1920,1080")

        # Suppress logging noise
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Headless mode
        if self.headless:
            options.add_argument("--headless=new")

        # Platform-specific adjustments
        system = platform.system()
        if system == "Linux":
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument("--single-process")
        elif system == "Darwin":
            # macOS specific
            if platform.machine() == "arm64":
                logger.info("Detected Apple Silicon (arm64).")

        # Performance
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.page_load_strategy = "normal"

        return options

    def get(self, url: str) -> None:
        """Navigate to a URL."""
        if not self.driver:
            raise RuntimeError("Browser not started. Call start() first.")
        self.driver.get(url)

    @property
def page_source(self) -> str:
        """Get current page HTML source."""
        if not self.driver:
            raise RuntimeError("Browser not started.")
        return self.driver.page_source

    def quit(self) -> None:
        """Safely close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed.")
            except Exception as exc:
                logger.warning("Error closing browser: %s", exc)
            finally:
                self.driver = None

    def __enter__(self) -> BrowserManager:
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.quit()