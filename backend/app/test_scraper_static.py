import asyncio
from app.scraper import scrape_static_site


async def test_static_scrape():
    url = "https://pages.github.com/"  # Try a static site
    result = await scrape_static_site(url)

    print("\n🔸 First 300 characters of HTML:\n")
    print(result["html"][:300])

    print("\n🔸 CSS Links:\n")
    for css in result["css_links"]:
        print(css)

    print("\n🔸 Image Sources:\n")
    for img in result["images"]:
        print(img)

if __name__ == "__main__":
    asyncio.run(test_static_scrape())
