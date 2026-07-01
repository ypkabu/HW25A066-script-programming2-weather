from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.weather_pipeline import aggregate_daily, build_api_url, load_json, write_outputs

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

    def test_invalid_lengths_raise_error(self) -> None:
        payload = json.loads(json.dumps(self.fixture))
        payload["hourly"]["temperature_2m"].pop()
        with self.assertRaises(ValueError):
            aggregate_daily(payload)


if __name__ == "__main__":
    unittest.main()
