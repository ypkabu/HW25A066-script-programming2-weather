from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output")
    required = [output / "weather_data.json", output / "weather_data.csv", output / "index.html"]
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
    for token in ["<!doctype html>", "出力データ一覧", "HW25A066", daily[0]["date"]]:
        if token not in html:
            print(f"[verify] token not found in HTML: {token}", file=sys.stderr)
            return 1

    summary = {
        "status": "SUCCESS",
        "daily_rows": len(daily),
        "files": {path.name: path.stat().st_size for path in required},
        "source": document.get("metadata", {}).get("source"),
    }
    (output / "build_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[verify] success: {len(daily)} rows, 3 primary artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
