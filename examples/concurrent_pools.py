"""Stress test: 30 URLs across 3 browser pools (2 headful + 1 headless).

Pool layout:

    Pool 0  headful   1 browser  10 tabs  → 10 URLs
    Pool 1  headful   1 browser  10 tabs  → 10 URLs
    Pool 2  headless  1 browser  10 tabs  → 10 URLs

All 30 tasks fire concurrently via asyncio.gather().  Each pool's
internal semaphore caps its own concurrency at 10 tabs, so the three
pools run fully in parallel — no global bottleneck.

Run::

    ./build.sh                              # build the Rust extension once
    uv run python examples/concurrent_pools.py

What you'll see:

    - 2 headful Chrome windows open (pools 0 and 1)
    - Results streaming in as each tab finishes
    - A summary table with per-pool latency stats
    - Total wall time much less than 30x single-tab time
"""

import asyncio
import time
from contextlib import AsyncExitStack
from dataclasses import dataclass, field

from voidcrawl import BrowserConfig, BrowserPool, PoolConfig

# ── URL set ──────────────────────────────────────────────────────────────
# Cycle 3 qscrape.dev test pages 10 times each = 30 URLs total.
_BASE_URLS = [
    "https://qscrape.dev/l2/news",
    "https://qscrape.dev/l2/scoretap",
    "https://qscrape.dev/l2/eshop",
]
URLS: list[str] = [_BASE_URLS[i % len(_BASE_URLS)] for i in range(30)]

# ── Pool configurations ───────────────────────────────────────────────────
POOL_CONFIGS = [
    PoolConfig(
        browsers=1,
        tabs_per_browser=10,
        browser=BrowserConfig(headless=False),  # headful #0
    ),
    PoolConfig(
        browsers=1,
        tabs_per_browser=10,
        browser=BrowserConfig(headless=False),  # headful #1
    ),
    PoolConfig(
        browsers=1,
        tabs_per_browser=10,
        browser=BrowserConfig(headless=True),  # headless
    ),
]


# ── Result dataclass ──────────────────────────────────────────────────────


@dataclass
class Result:
    url: str
    pool_idx: int
    title: str | None
    ok: bool
    elapsed_ms: float
    error: str | None = field(default=None)


# ── Per-fetch coroutine ───────────────────────────────────────────────────


async def fetch(pool: BrowserPool, pool_idx: int, url: str) -> Result:
    t0 = time.monotonic()
    try:
        async with pool.acquire() as tab:
            await tab.goto(url, timeout=30.0)
            title = await tab.title()
        return Result(
            url=url,
            pool_idx=pool_idx,
            title=title,
            ok=True,
            elapsed_ms=(time.monotonic() - t0) * 1000,
        )
    except Exception as exc:
        return Result(
            url=url,
            pool_idx=pool_idx,
            title=None,
            ok=False,
            elapsed_ms=(time.monotonic() - t0) * 1000,
            error=str(exc),
        )


# ── Main ──────────────────────────────────────────────────────────────────


async def main() -> None:
    pool_labels = ["headful-0", "headful-1", "headless"]

    async with AsyncExitStack() as stack:
        # ── Launch all 3 pools ────────────────────────────────────────
        print("Launching 3 Chrome pools...")
        pools: list[BrowserPool] = [
            await stack.enter_async_context(BrowserPool(cfg)) for cfg in POOL_CONFIGS
        ]
        for i, label in enumerate(pool_labels):
            print(f"  Pool {i}  {label:12s}  tabs_per_browser=10")

        # ── Warmup — pre-open all 30 tabs ─────────────────────────────
        print("\nWarming up (pre-opening tabs)...")
        t_warmup = time.monotonic()
        await asyncio.gather(*[p.warmup() for p in pools])
        print(f"  done in {(time.monotonic() - t_warmup) * 1000:.0f} ms")

        # ── Dispatch all 30 tasks ─────────────────────────────────────
        print(f"\nDispatching {len(URLS)} tasks...")
        tasks = [
            asyncio.create_task(fetch(pools[i % 3], i % 3, url))
            for i, url in enumerate(URLS)
        ]

        results: list[Result] = []
        t_start = time.monotonic()

        header = f"  {'#':>3}  {'pool':^10}  {'ms':>6}  {'ok':^4}  title"
        print(header)
        print("  " + "-" * (len(header) - 2))

        for n, done in enumerate(asyncio.as_completed(tasks), start=1):
            r: Result = await done
            results.append(r)
            status = "ok" if r.ok else "ERR"
            title_clip = (r.title or r.error or "")[:50]
            pool_label = pool_labels[r.pool_idx]
            print(
                f"  {n:>3}  {pool_label:^10}  {r.elapsed_ms:>6.0f}"
                f"  {status:^4}  {title_clip}"
            )

        total_ms = (time.monotonic() - t_start) * 1000

    # ── Summary ───────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"  Total wall time : {total_ms:.0f} ms  ({total_ms / 1000:.1f} s)")
    print(f"  URLs attempted  : {len(results)}")
    print(f"  Succeeded       : {sum(r.ok for r in results)}")
    print(f"  Failed          : {sum(not r.ok for r in results)}")

    print(f"\n  {'pool':^10}  {'ok':>4}  {'avg ms':>7}  {'min ms':>7}  {'max ms':>7}")
    print("  " + "-" * 44)
    for idx, label in enumerate(pool_labels):
        bucket = [r for r in results if r.pool_idx == idx]
        ok_bucket = [r for r in bucket if r.ok]
        if ok_bucket:
            avg = sum(r.elapsed_ms for r in ok_bucket) / len(ok_bucket)
            mn = min(r.elapsed_ms for r in ok_bucket)
            mx = max(r.elapsed_ms for r in ok_bucket)
            print(
                f"  {label:^10}  {len(ok_bucket):>4}"
                f"  {avg:>7.0f}  {mn:>7.0f}  {mx:>7.0f}"
            )
        else:
            print(f"  {label:^10}  {len(ok_bucket):>4}  {'—':>7}  {'—':>7}  {'—':>7}")


if __name__ == "__main__":
    asyncio.run(main())
