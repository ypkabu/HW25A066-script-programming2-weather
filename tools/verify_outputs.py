from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.weather_pipeline import write_artifact_manifest


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output")
    required = [
        output / "weather_data.json",
        output / "weather_data.csv",
        output / "index.html",
        output / "weather_alerts.json",
        output / "change_summary.json",
    ]
    missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
    if missing:
        print("[verify] missing or empty outputs:", *missing, sep="\n- ", file=sys.stderr)
        return 1

    document = json.loads((output / "weather_data.json").read_text(encoding="utf-8"))
    daily = document.get("daily", [])
    if not 1 <= len(daily) <= 7:
        print(f"[verify] unexpected daily row count: {len(daily)}", file=sys.stderr)
        return 1

    with (output / "weather_data.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(daily):
        print("[verify] JSON/CSV row counts differ", file=sys.stderr)
        return 1

    html = (output / "index.html").read_text(encoding="utf-8")
    for token in ["<!doctype html>", "出力データ一覧", "気象警告", "HW25A066", daily[0]["date"]]:
        if token not in html:
            print(f"[verify] token not found in HTML: {token}", file=sys.stderr)
            return 1

    alerts = json.loads((output / "weather_alerts.json").read_text(encoding="utf-8"))
    alert_counts = alerts.get("summary", {}).get("counts", {})
    for label in ["高温", "低温", "強い雨", "強風"]:
        if label not in alert_counts:
            print(f"[verify] alert count is missing: {label}", file=sys.stderr)
            return 1

    changes = json.loads((output / "change_summary.json").read_text(encoding="utf-8"))
    if "changed_days" not in changes or "comparisons" not in changes:
        print("[verify] change_summary.json is incomplete", file=sys.stderr)
        return 1

    summary = {
        "status": "SUCCESS",
        "daily_rows": len(daily),
        "files": {path.name: path.stat().st_size for path in required},
        "source": document.get("metadata", {}).get("source"),
        "alert_days": alerts.get("summary", {}).get("total_alert_days"),
        "changed_days": changes.get("changed_days"),
    }
    summary_path = output / "build_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest_path = write_artifact_manifest(output, [*required, summary_path])
    print(f"[verify] success: {len(daily)} rows, {len(required) + 2} artifacts")
    print(f"[verify] manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
