"""Built-in browser actions on qscrape.dev/l2/news (Mountainhome Herald).

Demonstrates composing a :class:`~voidcrawl.actions.Flow` from built-in
actions (:class:`~voidcrawl.actions.WaitForSelector`,
:class:`~voidcrawl.actions.GetText`,
:class:`~voidcrawl.actions.GetAttribute`) to scrape the first article
from a JS-rendered news feed.
"""

import asyncio

from voidcrawl import BrowserConfig, BrowserSession
from voidcrawl.actions import Flow, GetAttribute, GetText, WaitForSelector

TARGET_URL = "https://qscrape.dev/l2/news"


async def main() -> None:
    """Extract the first article headline and link from the news feed."""
    async with BrowserSession(BrowserConfig()) as browser:
        page = await browser.new_page(TARGET_URL)

        result = await (
            Flow()
            # WaitForSelector polls until the JS island has hydrated.
            .add(WaitForSelector(".hn-feed-item", timeout=15.0))
            # GetText reads textContent from the first matching element.
            .add(GetText(".hn-feed-headline"))
            # GetAttribute reads an HTML attribute; "src" from the first article image.
            .add(GetAttribute(".hn-feed-img", "src"))
        ).run(page)

        _waited, headline, img_src = result.results
        print(f"First headline : {headline}")
        print(f"First image    : {img_src}")


if __name__ == "__main__":
    asyncio.run(main())
