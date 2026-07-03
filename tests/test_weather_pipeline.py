from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.weather_pipeline import (
    aggregate_daily,
    build_api_url,
    build_change_summary,
    build_weather_alerts,
    load_json,
    write_artifact_manifest,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[1]


class WeatherPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_json(ROOT / "data" / "sample_open_meteo.json")

    def test_api_url_contains_required_fields(self) -> None:
        url = build_api_url(34.799, 135.356)
        self.assertIn("temperature_2m", url)
        self.assertIn("weather_code", url)
        self.assertIn("Asia%2FTokyo", url)

    def test_aggregate_daily_returns_seven_days(self) -> None:
        daily = aggregate_daily(self.fixture)
        self.assertEqual(7, len(daily))
        self.assertLessEqual(daily[0].temp_min_c, daily[0].temp_max_c)
        self.assertGreaterEqual(daily[0].humidity_avg_pct, 0)
        self.assertLessEqual(daily[0].humidity_avg_pct, 100)
        self.assertGreaterEqual(daily[0].wind_speed_max_kmh, 0)

    def test_write_outputs_json_and_csv(self) -> None:
        daily = aggregate_daily(self.fixture)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            json_path, csv_path = write_outputs(
                daily,
                out,
                location_name="宝塚市",
                latitude=34.799,
                longitude=135.356,
                source="test-fixture",
            )
            self.assertTrue(json_path.is_file())
            self.assertTrue(csv_path.is_file())
            document = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("HW25A066", document["metadata"]["student_id"])
            self.assertEqual(7, len(document["daily"]))
            self.assertIn("wind_speed_max_kmh", document["daily"][0])

    def test_invalid_lengths_raise_error(self) -> None:
        payload = json.loads(json.dumps(self.fixture))
        payload["hourly"]["temperature_2m"].pop()
        with self.assertRaises(ValueError):
            aggregate_daily(payload)

    def test_weather_alerts_include_all_required_categories(self) -> None:
        daily = aggregate_daily(self.fixture)
        alerts = build_weather_alerts(daily)
        self.assertIn("summary", alerts)
        for label in ["高温", "低温", "強い雨", "強風"]:
            self.assertIn(label, alerts["summary"]["counts"])

    def test_change_summary_compares_previous_build(self) -> None:
        daily = aggregate_daily(self.fixture)
        previous = {
            "daily": [
                {
                    "date": daily[0].date,
                    "temp_avg_c": daily[0].temp_avg_c - 1.0,
                    "precipitation_total_mm": daily[0].precipitation_total_mm,
                }
            ]
        }
        summary = build_change_summary(daily, previous)
        self.assertTrue(summary["previous_build_available"])
        self.assertGreaterEqual(summary["changed_days"], 1)

    def test_artifact_manifest_contains_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            path = out / "sample.txt"
            path.write_text("manifest-test", encoding="utf-8")
            manifest = write_artifact_manifest(out, [path])
            document = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual("sample.txt", document["artifacts"][0]["file_name"])
            self.assertEqual(64, len(document["artifacts"][0]["sha256"]))


if __name__ == "__main__":
    unittest.main()
