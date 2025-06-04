import asyncio
from app.scraper import scrape_website


async def test():
    # Test with a simple static site
    result = await scrape_website("https://example.com")
    print(f"\nScraper used: {result['scraper_used']}")
    print("\nHTML snippet:")
    print(result["html"][:500])
    print("\nCSS Links:")
    for css in result["css_links"]:
        print(css)
    print("\nImages:")
    for img in result["images"]:
        print(img)
    if result["screenshot"]:
        with open("screenshot.png", "wb") as f:
            f.write(result["screenshot"])
        print("\nScreenshot saved as screenshot.png")

asyncio.run(test())
