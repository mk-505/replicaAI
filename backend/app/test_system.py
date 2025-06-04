import asyncio
import requests
import json
from typing import Dict
import logging
from urllib.parse import urlparse
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to Python path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment variables (without showing actual values)
logger.info("Environment variables loaded:")
logger.info(
    f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")

# Test URLs - using simple, static sites for testing
TEST_URLS = [
    "https://example.com",  # Simple static site
    "https://httpbin.org/html",  # Static HTML endpoint
    "https://httpbin.org/status/200"  # Basic HTTP endpoint
]


async def test_scraping():
    """Test the scraping functionality using Playwright only"""
    logger.info("\n=== Testing Scraping (Playwright) ===")

    from app.scraper import scrape_website

    for url in TEST_URLS:
        try:
            logger.info(f"\nTesting scrape for: {url}")
            result = await scrape_website(url)

            # Check if we got the expected data
            assert result.get('html'), "No HTML content received"
            logger.info(
                f"✓ HTML content received ({len(result['html'])} chars)")

            if result.get('css_links'):
                logger.info(f"✓ Found {len(result['css_links'])} CSS links")

            if result.get('images'):
                logger.info(f"✓ Found {len(result['images'])} images")

            if result.get('screenshot'):
                logger.info(
                    f"✓ Screenshot captured ({len(result['screenshot'])} bytes)")

            logger.info("✓ Scraping successful")

        except Exception as e:
            logger.error(f"✗ Scraping failed for {url}: {str(e)}")
            raise


def test_llm_generation():
    """Test the LLM generation functionality"""
    logger.info("\n=== Testing LLM Generation ===")

    from app.llm_client import generate_clone_from_context

    # Check if Gemini API key is available
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY not set - skipping LLM generation test")
        return

    # Test context
    test_context = {
        'html': '<html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>',
        'css_links': ['https://example.com/style.css'],
        'images': ['https://example.com/image.jpg']
    }

    try:
        logger.info("Testing HTML generation with test context")
        result = generate_clone_from_context(test_context)

        # Log the first 200 characters of the result for debugging
        logger.info(f"Generated content preview: {result[:200]}...")

        # Check if we got valid HTML
        assert result, "No HTML generated"

        # Clean up the result for validation
        cleaned_result = result.strip()

        # Log the validation steps
        logger.info("Validating generated HTML...")

        # Check for common HTML patterns
        has_doctype = cleaned_result.startswith('<!DOCTYPE html>')
        has_html_tag = cleaned_result.startswith('<html>')
        has_head = '<head>' in cleaned_result
        has_body = '<body>' in cleaned_result

        logger.info(f"HTML validation results:")
        logger.info(f"- Has DOCTYPE: {has_doctype}")
        logger.info(f"- Has HTML tag: {has_html_tag}")
        logger.info(f"- Has HEAD section: {has_head}")
        logger.info(f"- Has BODY section: {has_body}")

        # Validate the structure
        assert has_doctype or has_html_tag, "Generated content must start with DOCTYPE or HTML tag"
        assert has_head, "Generated content must contain a HEAD section"
        assert has_body, "Generated content must contain a BODY section"

        logger.info(f"✓ Generated HTML ({len(result)} chars)")
        logger.info("✓ LLM generation successful")

    except Exception as e:
        logger.error(f"✗ LLM generation failed: {str(e)}")
        if 'result' in locals():
            logger.error(f"Generated content: {result}")
        raise


def test_api_endpoints():
    """Test the API endpoints"""
    logger.info("\n=== Testing API Endpoints ===")

    base_url = "http://localhost:8000"

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        logger.info("✓ Root endpoint working")
    except Exception as e:
        logger.error(f"✗ Root endpoint failed: {str(e)}")
        raise

    # Test scrape endpoint
    try:
        for url in TEST_URLS:
            logger.info(f"\nTesting scrape endpoint with: {url}")
            response = requests.post(
                f"{base_url}/scrape",
                json={"target_url": url}
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get('html'), "No HTML in response"
            logger.info(f"✓ Scrape endpoint successful for {url}")
    except Exception as e:
        logger.error(f"✗ Scrape endpoint failed: {str(e)}")
        raise

    # Test clone endpoint
    try:
        for url in TEST_URLS:
            logger.info(f"\nTesting clone endpoint with: {url}")
            response = requests.post(
                f"{base_url}/clone",
                json={"target_url": url}
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get('cloned_html'), "No cloned HTML in response"
            logger.info(f"✓ Clone endpoint successful for {url}")
    except Exception as e:
        logger.error(f"✗ Clone endpoint failed: {str(e)}")
        raise


async def run_all_tests():
    """Run all tests"""
    try:
        # Test scraping
        await test_scraping()

        # Test LLM generation
        test_llm_generation()

        # Test API endpoints
        test_api_endpoints()

        logger.info("\n=== All tests completed successfully! ===")

    except Exception as e:
        logger.error(f"\n=== Tests failed: {str(e)} ===")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())
