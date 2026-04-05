#!/usr/bin/env bash
# VoidCrawl headless Chrome entrypoint.
# Generates a supervisord.conf from voidcrawl.scale at container start so the
# Chrome farm is sized to match available memory, CPU, and file-descriptor limits.
#
# Environment variables:
#   SCALE_PROFILE   — minimal | balanced (default) | advanced
#   CHROME_WS_URLS  — if already set, skip scale computation (passthrough mode)
set -euo pipefail

SCALE_PROFILE="${SCALE_PROFILE:-balanced}"
CONF_PATH=/tmp/supervisord-dynamic.conf

# If the caller already hard-coded CHROME_WS_URLS (e.g. PoolConfig.from_docker),
# bypass scale computation and fall back to the static config.
if [[ -n "${CHROME_WS_URLS:-}" ]]; then
    echo "[entrypoint] CHROME_WS_URLS is set — using static supervisord config"
    exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi

echo "[entrypoint] Scale profile: ${SCALE_PROFILE}"

python3 - <<'PYEOF'
import os, sys
from voidcrawl.scale import compute_scale, generate_supervisord_conf, InsufficientResourcesError

profile = os.environ.get("SCALE_PROFILE", "balanced")
conf_path = os.environ.get("_VC_CONF_PATH", "/tmp/supervisord-dynamic.conf")

try:
    report = compute_scale(profile=profile)
except InsufficientResourcesError as exc:
    print(f"[entrypoint] ERROR: {exc}", file=sys.stderr)
    sys.exit(1)

report.print_report()

conf = generate_supervisord_conf(report)
open(conf_path, "w").write(conf)

ws_urls = ",".join(
    f"http://localhost:{9222 + i}" for i in range(report.browsers)
)
# Write env vars to a file so the shell can source them
with open("/tmp/vc-env.sh", "w") as fh:
    fh.write(f"export CHROME_WS_URLS={ws_urls}\n")
    fh.write(f"export BROWSER_COUNT={report.browsers}\n")
    fh.write(f"export TABS_PER_BROWSER={report.tabs_per_browser}\n")
    fh.write(f"export TAB_MAX_IDLE_SECS={report.tab_max_idle_secs}\n")
    fh.write(f"export CHROME_HEADLESS={'1' if report.headless else '0'}\n")
PYEOF

# Export computed vars into the current shell environment
# shellcheck source=/dev/null
source /tmp/vc-env.sh

echo "[entrypoint] Launching ${BROWSER_COUNT} Chrome instance(s) via supervisord"
exec supervisord -c "${CONF_PATH}"
