from app.llm_client import generate_clone_from_context
from .scraper import scrape_website
import asyncio
import time
import base64
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
import requests
print("Requests imported successfully!")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    target_url: HttpUrl


class ScrapeResponse(BaseModel):
    status: str
    url: str
    scraper_used: str
    html: str
    css_links: list[str]
    images: list[str]
    screenshot: Optional[str] = None  # Base64 encoded if present
    inline_styles: list[str] = []
    scripts: list[str] = []
    meta_tags: list[dict] = []
    processing_time: float  # Time taken to process the request


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(request: ScrapeRequest):
    start_time = time.time()
    try:
        logger.info(f"Received scrape request for URL: {request.target_url}")
        try:
            result = await asyncio.wait_for(
                scrape_website(str(request.target_url)),
                timeout=15.0  # 15 second timeout for the entire operation
            )
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logger.error(
                f"Scraping operation timed out after {elapsed:.2f} seconds")
            raise HTTPException(
                status_code=504,
                detail="Scraping operation timed out"
            )

        # Convert screenshot to base64 if present
        screenshot_base64 = None
        if result.get('screenshot'):
            logger.info("Converting screenshot to base64")
            screenshot_base64 = base64.b64encode(
                result['screenshot']).decode('utf-8')

        elapsed = time.time() - start_time
        logger.info(f"Total request processing time: {elapsed:.2f} seconds")
        return ScrapeResponse(
            status="success",
            url=str(request.target_url),
            scraper_used=result.get('scraper_used', 'playwright'),
            html=result.get('html', ''),
            css_links=result.get('css_links', []),
            images=result.get('images', []),
            screenshot=screenshot_base64,
            inline_styles=result.get('inline_styles', []),
            scripts=result.get('scripts', []),
            meta_tags=result.get('meta_tags', []),
            processing_time=elapsed
        )
    except Exception as e:
        logger.error(f"Error in /scrape endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape website: {str(e)}"
        )


class CloneRequest(BaseModel):
    target_url: HttpUrl


class CloneResponse(BaseModel):
    cloned_html: str


@app.post("/clone", response_model=CloneResponse)
async def clone_endpoint(request: CloneRequest):
    try:
        logger.info(f"Received clone request for URL: {request.target_url}")
        # Scrape the website using Playwright
        try:
            scrape_result = await asyncio.wait_for(
                scrape_website(str(request.target_url)),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.error("Scraping operation timed out")
            raise HTTPException(
                status_code=504,
                detail="Scraping operation timed out"
            )

        # Prepare context for the LLM
        context = {
            'html': scrape_result['html'],
            'css_links': scrape_result['css_links'],
            'images': scrape_result['images'],
        }
        # Add screenshot if present
        if scrape_result.get('screenshot'):
            context['screenshot_base64'] = base64.b64encode(
                scrape_result['screenshot']).decode('utf-8')

        # Generate the clone
        try:
            cloned_html = generate_clone_from_context(context)
            if not cloned_html or not cloned_html.strip():
                raise ValueError("Generated HTML is empty")
        except Exception as e:
            logger.error(f"Error generating clone: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate clone: {str(e)}"
            )
        return CloneResponse(cloned_html=cloned_html)
    except Exception as e:
        logger.error(f"Error in /clone endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process clone request: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
