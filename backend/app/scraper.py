from typing import Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_with_playwright(url: str) -> Dict[str, any]:
    """
    Scrape a website using Playwright (headless browser).
    Extract HTML, CSS links, images, inline styles, scripts, meta tags, and screenshot.
    """
    start_time = time.time()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logger.debug(f"Navigating to {url} with Playwright")
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html = await page.content()
            screenshot_bytes = await page.screenshot(full_page=True)
            await browser.close()

        soup = BeautifulSoup(html, 'html.parser')

        # Extract CSS links
        css_links = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_links.append(urljoin(url, href))

        # Extract image sources
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(urljoin(url, src))

        # Extract inline <style> tags
        inline_styles = [style.get_text() for style in soup.find_all('style')]

        # Extract <script> tags
        scripts = [script.get_text() for script in soup.find_all('script')]

        # Extract meta tags
        meta_tags = [dict(meta.attrs) for meta in soup.find_all('meta')]

        elapsed = time.time() - start_time
        logger.debug(f"Playwright scrape completed in {elapsed:.2f} seconds")
        return {
            'html': html,
            'css_links': css_links,
            'images': images,
            'inline_styles': inline_styles,
            'scripts': scripts,
            'meta_tags': meta_tags,
            'screenshot': screenshot_bytes,
            'scraper_used': 'playwright'
        }

    except PlaywrightTimeoutError:
        logger.error(f"Timeout while scraping {url} with Playwright")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while scraping {url} with Playwright: {str(e)}")
        raise


async def scrape_website(url: str) -> Dict[str, any]:
    """
    Scrape a website using Playwright for all content and screenshot.
    Args:
        url (str): The URL to scrape
    Returns:
        Dict containing html, css_links, images, etc.
    """
    return await scrape_with_playwright(url)
