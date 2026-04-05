"""Performance modes: size a pool to your hardware with scale profiles.

VoidCrawl ships three built-in profiles that measure available RAM, CPU
cores, and file-descriptor limits, then return a :class:`~voidcrawl.PoolConfig`
sized for the requested aggressiveness:

* ``"minimal"``   — CI runners, Raspberry Pi, embedded (1 browser, 2 tabs, headless)
* ``"balanced"``  — developer laptops / desktop PCs (default)
* ``"advanced"``  — dedicated servers (uses up to 90 % of RAM)

This example shows three ways to use profiles:

1. ``PoolConfig.from_profile()``  — one-liner for common usage
2. ``compute_scale()``            — inspect the full ScaleReport
3. ``detect_resources()``         — raw hardware snapshot, useful for debugging

Run::

    uv run python examples/performance_modes.py
    uv run python examples/performance_modes.py --profile advanced
    uv run python examples/performance_modes.py --dry-run   # no browser launch
"""

import argparse
import asyncio

from voidcrawl import BrowserPool, PoolConfig, ScaleProfile
from voidcrawl.scale import InsufficientResourcesError, compute_scale, detect_resources

TARGET_URL = "https://qscrape.dev/l2/news"


# ── 1. Raw resource snapshot ─────────────────────────────────────────────


def show_resources() -> None:
    """Print the raw hardware snapshot without computing a profile."""
    snap = detect_resources()
    print("Hardware snapshot")
    print(
        f"  RAM        : {snap.free_ram_mb:,} MB free / {snap.total_ram_mb:,} MB total"
    )
    print(f"  Effective  : {snap.effective_ram_mb:,} MB (cgroup limit applied if set)")
    print(f"  CPU cores  : {snap.cpu_cores}")
    print(f"  Load avg   : {snap.load_avg_1m:.2f}")
    print(f"  Swap used  : {snap.swap_used_mb:,} MB")
    print(f"  FD limit   : {snap.fd_soft_limit:,}")
    print(f"  Display    : {'yes' if snap.has_display else 'no'}")
    print(f"  Container  : {'yes' if snap.in_container else 'no'}")
    if snap.cgroup_mem_limit_mb is not None:
        print(f"  cgroup cap : {snap.cgroup_mem_limit_mb:,} MB")


# ── 2. Full ScaleReport via compute_scale() ──────────────────────────────


def show_report(profile: ScaleProfile) -> PoolConfig:
    """Compute a pool config for *profile* and print the full report."""
    try:
        report = compute_scale(profile=profile)
    except InsufficientResourcesError as exc:
        print(f"Cannot use profile {profile!r}: {exc}")
        raise SystemExit(1) from exc

    report.print_report()  # rich-formatted table when rich is installed

    if report.warnings:
        # compute_scale() may downgrade the profile (e.g. advanced → balanced
        # when swap is active).  The actual resolved profile is in report.profile.
        print(
            f"\nNote: effective profile is {report.profile!r} (requested {profile!r})"
        )

    return report.to_pool_config()


# ── 3. One-liner via PoolConfig.from_profile() ───────────────────────────


async def run_with_profile(profile: ScaleProfile, dry_run: bool) -> None:
    """Fetch a page using a pool sized by *profile*."""
    # from_profile() calls compute_scale internally — use it when you
    # don't need to inspect the report.
    pool_cfg = PoolConfig.from_profile(profile)
    print(
        f"\nPoolConfig from {profile!r} profile:"
        f"  browsers={pool_cfg.browsers}"
        f"  tabs={pool_cfg.tabs_per_browser}"
        f"  headless={pool_cfg.browser.headless}"
        f"  idle_secs={pool_cfg.tab_max_idle_secs}"
    )

    if dry_run:
        print("  (--dry-run: skipping browser launch)")
        return

    print(f"\nFetching {TARGET_URL} ...")
    async with BrowserPool(pool_cfg) as pool, pool.acquire() as tab:
        await tab.goto(TARGET_URL, timeout=30.0)
        title = await tab.title()
        html = await tab.content()
    print(f"  Title       : {title}")
    print(f"  HTML length : {len(html):,} chars")


# ── 4. All three profiles side-by-side (dry run) ─────────────────────────


def compare_profiles() -> None:
    """Print the pool configs all three profiles would produce on this machine."""
    snap = detect_resources()
    print("\nProfile comparison on this machine:")
    header = (
        f"  {'profile':10s}  {'browsers':>9}"
        f"  {'tabs/browser':>12}  {'total tabs':>10}  {'headless':>8}"
    )
    print(header)
    print("  " + "-" * 58)
    for p in ("minimal", "balanced", "advanced"):
        try:
            report = compute_scale(profile=p, snapshot=snap)  # type: ignore[arg-type]
        except InsufficientResourcesError:
            print(f"  {p:10s}  (insufficient resources)")
            continue
        print(
            f"  {p:10s}  {report.browsers:>9}  {report.tabs_per_browser:>12}"
            f"  {report.total_tabs:>10}  {report.headless!r:>8}"
        )


# ── main ──────────────────────────────────────────────────────────────────


async def main() -> None:
    parser = argparse.ArgumentParser(description="VoidCrawl performance modes demo")
    parser.add_argument(
        "--profile",
        choices=["minimal", "balanced", "advanced"],
        default="balanced",
        help="Scale profile to use (default: balanced)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the scale report and pool config without launching a browser",
    )
    args = parser.parse_args()
    profile: ScaleProfile = args.profile  # type: ignore[assignment]

    # ── Step 1: raw snapshot ──────────────────────────────────────────────
    print("=" * 50)
    show_resources()

    # ── Step 2: full report for the chosen profile ────────────────────────
    print("\n" + "=" * 50)
    show_report(profile)

    # ── Step 3: compare all profiles on this machine ──────────────────────
    compare_profiles()

    # ── Step 4: actually run (or skip with --dry-run) ─────────────────────
    print("\n" + "=" * 50)
    await run_with_profile(profile, dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
