from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.weather_pipeline import (
    aggregate_daily,
    build_api_url,
    fetch_weather_json,
    load_json,
    write_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="天気データを取得し、JSON/CSVへ出力します。")
    parser.add_argument("--location", default="宝塚市")
    parser.add_argument("--latitude", type=float, default=34.7990)
    parser.add_argument("--longitude", type=float, default=135.3560)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--fixture", type=Path, default=Path("data/sample_open_meteo.json"))
    parser.add_argument("--offline", action="store_true", help="APIに接続せずfixtureを使用")
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="API取得失敗時にfixtureへ切り替えず終了",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source: str
    if args.offline:
        payload = load_json(args.fixture)
        source = f"fixture:{args.fixture.as_posix()}"
        print(f"[weather] offline mode: {args.fixture}")
    else:
        url = build_api_url(args.latitude, args.longitude)
        print(f"[weather] requesting Open-Meteo for {args.location}")
        try:
            payload = fetch_weather_json(url)
            source = "Open-Meteo Forecast API"
            print("[weather] live API request succeeded")
        except Exception as exc:  # ネットワーク障害時も課題デモを止めない
            if args.no_fallback:
                print(f"[weather] API request failed: {exc}", file=sys.stderr)
                return 1
            print(f"[weather] API request failed; use fixture instead: {exc}")
            payload = load_json(args.fixture)
            source = f"fixture-fallback:{args.fixture.as_posix()}"

    daily = aggregate_daily(payload)
    if not daily:
        print("[weather] no daily records were generated", file=sys.stderr)
        return 1
    json_path, csv_path = write_outputs(
        daily,
        args.output_dir,
        location_name=args.location,
        latitude=args.latitude,
        longitude=args.longitude,
        source=source,
    )
    print(f"[weather] generated {len(daily)} days")
    print(f"[weather] JSON: {json_path}")
    print(f"[weather] CSV : {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
