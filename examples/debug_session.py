"""Interactive step debugger via BrowserConfig.

Pass ``debug=True`` to :class:`BrowserConfig` and every
:meth:`Flow.run` call against that session's pages will automatically
pause before each action with an interactive prompt.

Debugger key bindings
---------------------
n / Enter   execute current action and advance
c           continue running until the end
b           rewind one step (re-navigates and replays)
r           restart from the beginning
l           list all queued actions with position marker
h           show history of executed actions and results
q           quit the session early

Run this example
----------------
    python examples/debug_session.py

Uses qscrape.dev/l2/taxes (Eldoria Registry of Deeds) — a JS-rendered
search form whose DOM is only available after hydration.
"""

import asyncio

from voidcrawl import BrowserConfig, BrowserSession
from voidcrawl.actions import (
    ClickElement,
    Flow,
    GetText,
    SetInputValue,
    WaitForSelector,
)

TARGET_URL = "https://qscrape.dev/l2/taxes"


async def main() -> None:
    # headless=False lets you see the red highlight flash on each targeted element.
    # stepping=False runs without pausing (default is True — pause before every step).
    cfg = BrowserConfig(headless=False, debug=True, stepping=True, highlight=True)

    async with BrowserSession(cfg) as browser:
        page = await browser.new_page(TARGET_URL)

        flow = (
            Flow()
            .add(WaitForSelector(".er-input"))
            .add(SetInputValue(".er-input", "Armok"))
            .add(ClickElement(".er-btn-primary"))
            .add(WaitForSelector(".er-row"))
            .add(GetText(".er-row"))
        )

        result = await flow.run(page)
        print(f"\nCollected results: {result.results}")


if __name__ == "__main__":
    asyncio.run(main())
