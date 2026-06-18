import asyncio

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from config.settings import settings
from src.utils.logger import logger
from src.utils.rate_limiter import rate_limiter

class LinkedInBrowser:
    """
    Manages a stealth Playwright Chromium session for LinkedIn.

    Usage:
        browser = LinkedInBrowser()
        await browser.start()
        html = await browser.get_rendered_html("https://www.linkedin.com/in/someone/")
        await browser.close()
    """

    def __init__(self):
        self._playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def start(self):
        """Launch the browser and log in to LinkedIn."""
        logger.info("Starting browser...")
        self._playwright = await async_playwright().start()

        self.browser = await self._playwright.chromium.launch(
            headless=settings.HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ],
        )

        # Realistic browser context
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width" : 1280 , "height" : 900},
            locale="en-US",
            timezone_id="America/New_York",
        )

        # Stealth: hide the 'webdriver' flag that LinkedIn checks for
        await self.context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.page = await self.context.new_page()
        await self._login()

    async def _login(self):
        """Authenticate with LinkedIn credentials from .env."""
        logger.info("Logging in to LinkedIn")

        await self.page.goto(
            "https://www.linkedin.com/login",
            wait_until="domcontentloaded",
            timeout=20000,
        )

        # Type credentials with slight delays to mimic human typing
        await self.page.fill("#username", settings.LINKEDIN_EMAIL)
        await asyncio.sleep(0.4)
        await self.page.fill("#password", settings.LINKEDIN_PASSWORD)
        await asyncio.sleep(0.3)
        await self.page.click('[type="submit"]')

        try:
            await self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass  # Sometimes networkidle times out on slow connections

        current_url = self.page.url

        if any(x in current_url for x in ["checkpoint", "challenge", "captcha"]): #Checks for security checks
            logger.error("LinkedIn security challenge detected!")
            if settings.HEADLESS:
                raise RuntimeError(
                    "LinkedIn challenged the login. "
                    "Set HEADLESS=false in .env and retry to solve it manually."
                )
            else:
                logger.warning("⏳ Waiting 60s for manual CAPTCHA solve...")
                await asyncio.sleep(60)

        logger.info("Login successful.")


    async def get_rendered_html(self, url: str) -> str:
        """
        Navigate to a LinkedIn URL, trigger lazy-loaded content by
        scrolling, and return the fully rendered HTML for BeautifulSoup.
        """
        await rate_limiter.wait()
        logger.info(f" Fetching → {url}")

        await self.page.goto(url, wait_until="networkidle", timeout=30000)

        # Scroll down in steps to trigger lazy content
        for scroll_frac in [0.3, 0.6, 0.9, 1.0]:
            await self.page.evaluate(
                f"window.scrollTo(0, document.body.scrollHeight * {scroll_frac})"
            )
            await asyncio.sleep(0.8)

        # Scroll back to top for a natural feel
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

        return await self.page.content()

    async def close(self):
        """Shut down the browser and Playwright cleanly."""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed.")