"""Stealth mode — full matrix demonstration.

Tests VoidCrawl's stealth across a 2x2 matrix of (headless/headful) x
(stealth OFF/ON) against three targets:

  1. BusinessWire (Akamai WAF) — real-world anti-bot protection.
  2. QScrape L3 (our anti-bot test suite at qscrape.dev/l3/scoretap).
  3. Fingerprint signals — what bot-detection scripts see in each mode.

Requires a display for headful tests — run on a desktop, or use
Docker headful (see examples/docker_headful.py).
"""

import asyncio
import json
import textwrap

from voidcrawl import BrowserConfig, BrowserSession

# ── Targets ──────────────────────────────────────────────────────────────

BUSINESSWIRE_URL = (
    "https://www.businesswire.com/news/home/20251114087859/en/"
    "Latin-America-AI-in-Payments-and-E-Commerce-Analysis-Report-2025-"
    "Featuring-OpenAI-Google-Anthropic-Galileo-JPMorgan-Pix-and-Latitud-"
    "--ResearchAndMarkets.com"
)
L3_URL = "https://qscrape.dev/l3/scoretap"

FINGERPRINT_JS = """
JSON.stringify({
    webdriver: navigator.webdriver,
    plugins_count: navigator.plugins.length,
    languages: navigator.languages,
    has_chrome_runtime: typeof window.chrome !== 'undefined'
        && typeof window.chrome.runtime !== 'undefined',
    inner_viewport: window.innerWidth + 'x' + window.innerHeight,
})
"""

# ── Matrix ───────────────────────────────────────────────────────────────

MATRIX = [
    {"headless": True, "stealth": False},
    {"headless": True, "stealth": True},
    {"headless": False, "stealth": False},
    {"headless": False, "stealth": True},
]


def mode_label(headless: bool, stealth: bool) -> str:
    h = "headless" if headless else "headful "
    s = "stealth=ON " if stealth else "stealth=OFF"
    return f"{h} {s}"


def banner(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def result_line(label: str, ok: bool, detail: str) -> None:
    mark = "✓" if ok else "✗"
    print(f"  [{label}]  {detail}  {mark}")


# ── 1. BusinessWire (Akamai WAF) ────────────────────────────────────────


async def test_businesswire() -> None:
    banner("Target 1: BusinessWire (Akamai WAF)")

    for combo in MATRIX:
        headless, stealth = combo["headless"], combo["stealth"]
        label = mode_label(headless, stealth)
        try:
            cfg = BrowserConfig(stealth=stealth, headless=headless)
            async with BrowserSession(cfg) as browser:
                page = await browser.new_page(BUSINESSWIRE_URL)
                await page.wait_for_network_idle(timeout=20.0)
                html = await page.content()
                title = await page.title()
                blocked = "access denied" in html.lower() or "403" in (title or "")
                snippet = title or html[:80]
                result_line(label, not blocked, f"Title: {snippet!r:.60}")
                if not blocked:
                    print(f"           Body: {len(html):,} chars")
        except Exception as exc:
            result_line(label, False, f"Blocked/Error: {exc}")


# ── 2. QScrape L3 (anti-bot suite) ──────────────────────────────────────


async def test_l3() -> None:
    banner("Target 2: QScrape L3 (anti-bot suite)")

    for combo in MATRIX:
        headless, stealth = combo["headless"], combo["stealth"]
        label = mode_label(headless, stealth)
        try:
            cfg = BrowserConfig(stealth=stealth, headless=headless)
            async with BrowserSession(cfg) as browser:
                page = await browser.new_page(L3_URL)
                await page.wait_for_network_idle(timeout=15.0)
                await asyncio.sleep(2.0)
                html = await page.content()
                title = await page.title()
                got_404 = "404" in (title or "") or "404" in html[:500]
                result_line(label, not got_404, f"Title: {title!r}")
                if not got_404:
                    print(f"           Body: {len(html):,} chars")
        except Exception as exc:
            result_line(label, False, f"Error: {exc}")


# ── 3. Fingerprint signals ──────────────────────────────────────────────


async def test_fingerprints() -> None:
    banner("Target 3: Fingerprint signals")

    for combo in MATRIX:
        headless, stealth = combo["headless"], combo["stealth"]
        label = mode_label(headless, stealth)
        try:
            cfg = BrowserConfig(stealth=stealth, headless=headless)
            async with BrowserSession(cfg) as browser:
                page = await browser.new_page("about:blank")
                raw = await page.evaluate_js(FINGERPRINT_JS)
                fp = json.loads(str(raw))
                print(f"\n  [{label}]")
                for key, value in fp.items():
                    print(f"    {key}: {value}")
        except Exception as exc:
            print(f"\n  [{label}]  Error: {exc}")


# ── Main ─────────────────────────────────────────────────────────────────


async def main() -> None:
    print(
        textwrap.dedent("""\
        VoidCrawl stealth mode — full matrix demonstration
        --------------------------------------------------
        Matrix: headless/headful x stealth OFF/ON (4 combinations)
        """)
    )
    await test_businesswire()
    await test_l3()
    await test_fingerprints()

    print(f"\n{'─' * 60}")
    print("  Done. Compare results across all four mode combinations.")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
