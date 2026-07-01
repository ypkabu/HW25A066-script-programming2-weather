from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    status = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("[discord] DISCORD_WEBHOOK_URL is not configured; notification skipped")
        return 0

    job_name = os.environ.get("JOB_NAME", "weather-dashboard")
    build_number = os.environ.get("BUILD_NUMBER", "local")
    build_url = os.environ.get("BUILD_URL", "")
    icon = "✅" if status.upper() == "SUCCESS" else "❌"
    text = f"{icon} Jenkins {status}: {job_name} #{build_number}"
    if build_url:
        text += f"\n{build_url}"
    body = json.dumps({"content": text}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "Jenkins-weather-dashboard"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status not in (200, 204):
            raise RuntimeError(f"Discord returned HTTP {response.status}")
    print("[discord] notification sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
