"""Custom inline-JS actions on qscrape.dev/l2/eshop (VaultMart).

Demonstrates creating a custom :class:`~voidcrawl.actions.JsActionNode`
with :func:`~voidcrawl.actions.inline_js` to extract structured product
data from a JS-rendered e-commerce page.
"""

import asyncio

from voidcrawl import BrowserConfig, BrowserSession
from voidcrawl.actions import Flow, JsActionNode, inline_js

TARGET_URL = "https://qscrape.dev/l2/eshop"


class ExtractProducts(JsActionNode):
    """Pull all product badge items and their prices from the hydrated DOM."""

    js = inline_js(
        """
        return Array.from(document.querySelectorAll('.vm-pbadge-item')).map(el => ({
            name:     (el.querySelector('.vm-pbadge-name') || {}).textContent || null,
            sale:     (el.querySelector('.vm-pbadge-sale') || {}).textContent || null,
            original: (el.querySelector('.vm-pbadge-orig') || {}).textContent || null,
            discount: (el.querySelector('.vm-pbadge-disc') || {}).textContent || null,
        }));
        """
    )


async def main() -> None:
    """Scrape VaultMart products using a custom inline JS action."""
    async with BrowserSession(BrowserConfig()) as browser:
        page = await browser.new_page(TARGET_URL)
        await page.wait_for_network_idle()

        result = await Flow().add(ExtractProducts()).run(page)
        products: list[dict[str, str | None]] = result.last  # type: ignore[assignment]

        print(f"Found {len(products)} product(s):\n")
        for p in products:
            name = p.get("name") or "(no name)"
            sale = (p.get("sale") or "").strip()
            orig = (p.get("original") or "").strip()
            disc = (p.get("discount") or "").strip()

            price = sale
            if orig:
                price += f"  (was {orig})"
            if disc:
                price += f"  [{disc} off]"
            print(f"  {name}: {price.strip() or 'n/a'}")


if __name__ == "__main__":
    asyncio.run(main())
