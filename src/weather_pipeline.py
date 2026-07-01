from __future__ import annotations

import csv
import json
import math
import statistics
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

WEATHER_LABELS = {
    0: "快晴",
    1: "晴れ",
    2: "一部くもり",
    3: "くもり",
    45: "霧",
    48: "着氷性の霧",
    51: "弱い霧雨",
    53: "霧雨",
    55: "強い霧雨",
    56: "弱い着氷性霧雨",
    57: "強い着氷性霧雨",
    61: "弱い雨",
    63: "雨",
    65: "強い雨",
    66: "弱い着氷性の雨",
    67: "強い着氷性の雨",
    71: "弱い雪",
    73: "雪",
    75: "強い雪",
    77: "霧雪",
    80: "弱いにわか雨",
    81: "にわか雨",
    82: "激しいにわか雨",
    85: "弱いにわか雪",
    86: "強いにわか雪",
    95: "雷雨",
    96: "ひょうを伴う雷雨",
    99: "激しいひょうを伴う雷雨",
}


@dataclass(frozen=True)
class DailyWeather:
    date: str
    temp_min_c: float
    temp_max_c: float
    temp_avg_c: float
    humidity_avg_pct: float
    precipitation_total_mm: float
    precipitation_probability_max_pct: float
    weather_code: int
    weather: str


def build_api_url(latitude: float, longitude: float, timezone: str = "Asia/Tokyo") -> str:
    params = {
        "latitude": f"{latitude:.6f}",
        "longitude": f"{longitude:.6f}",
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
            ]
        ),
        "forecast_days": "7",
        "timezone": timezone,
    }
    return "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)


def fetch_weather_json(url: str, timeout_seconds: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HW25A066-script-programming2/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        if response.status != 200:
            raise RuntimeError(f"Weather API returned HTTP {response.status}")
        payload = json.loads(response.read().decode("utf-8"))
    if "hourly" not in payload:
        raise ValueError("Weather API response does not contain hourly data")
    return payload


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _dominant_code(codes: Iterable[int]) -> int:
    counts = Counter(int(code) for code in codes)
    if not counts:
        return 0
    # 同数なら、より悪天候側（数値が大きい方）を採用して見落としを避ける。
    return max(counts.items(), key=lambda item: (item[1], item[0]))[0]


def aggregate_daily(payload: dict[str, Any]) -> list[DailyWeather]:
    hourly = payload.get("hourly") or {}
    required = [
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "precipitation",
        "weather_code",
    ]
    missing = [key for key in required if key not in hourly]
    if missing:
        raise ValueError(f"Missing hourly fields: {', '.join(missing)}")

    lengths = {key: len(hourly[key]) for key in required}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"Hourly field lengths differ: {lengths}")

    grouped: dict[str, dict[str, list[float | int]]] = defaultdict(
        lambda: {
            "temperature": [],
            "humidity": [],
            "precip_probability": [],
            "precipitation": [],
            "weather_code": [],
        }
    )

    for index, timestamp in enumerate(hourly["time"]):
        date = str(timestamp)[:10]
        grouped[date]["temperature"].append(_safe_float(hourly["temperature_2m"][index]))
        grouped[date]["humidity"].append(_safe_float(hourly["relative_humidity_2m"][index]))
        grouped[date]["precip_probability"].append(
            _safe_float(hourly["precipitation_probability"][index])
        )
        grouped[date]["precipitation"].append(_safe_float(hourly["precipitation"][index]))
        grouped[date]["weather_code"].append(int(_safe_float(hourly["weather_code"][index])))

    daily: list[DailyWeather] = []
    for date in sorted(grouped):
        row = grouped[date]
        temperatures = [float(v) for v in row["temperature"]]
        humidities = [float(v) for v in row["humidity"]]
        probabilities = [float(v) for v in row["precip_probability"]]
        precipitation = [float(v) for v in row["precipitation"]]
        codes = [int(v) for v in row["weather_code"]]
        code = _dominant_code(codes)
        daily.append(
            DailyWeather(
                date=date,
                temp_min_c=round(min(temperatures), 1),
                temp_max_c=round(max(temperatures), 1),
                temp_avg_c=round(statistics.fmean(temperatures), 1),
                humidity_avg_pct=round(statistics.fmean(humidities), 1),
                precipitation_total_mm=round(sum(precipitation), 1),
                precipitation_probability_max_pct=round(max(probabilities), 1),
                weather_code=code,
                weather=WEATHER_LABELS.get(code, f"不明({code})"),
            )
        )
    return daily


def write_outputs(
    daily: list[DailyWeather],
    output_dir: Path,
    *,
    location_name: str,
    latitude: float,
    longitude: float,
    source: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    json_path = output_dir / "weather_data.json"
    csv_path = output_dir / "weather_data.csv"

    document = {
        "metadata": {
            "student_id": "HW25A066",
            "student_name": "嶋田一歩",
            "location": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "generated_at": generated_at,
            "source": source,
            "days": len(daily),
        },
        "daily": [asdict(item) for item in daily],
    }
    json_path.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = list(asdict(daily[0]).keys()) if daily else []
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in daily:
            writer.writerow(asdict(item))

    return json_path, csv_path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
