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
    git_commit = os.environ.get("GIT_COMMIT", os.environ.get("GIT_COMMIT_SHORT", "unknown"))
    if len(git_commit) > 12:
        git_commit = git_commit[:12]
    icon = "✅" if status.upper() == "SUCCESS" else "❌"
    text = "\n".join(
        [
            f"{icon} Jenkins build notification",
            f"Job: {job_name}",
            f"Build: #{build_number}",
            f"Status: {status.upper()}",
            f"Git commit: {git_commit}",
            f"Build URL: {build_url or 'not available'}",
        ]
    )
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
