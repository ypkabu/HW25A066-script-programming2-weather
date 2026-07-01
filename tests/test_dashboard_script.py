from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.weather_pipeline import aggregate_daily, load_json, write_outputs

ROOT = Path(__file__).resolve().parents[1]


class DashboardScriptTests(unittest.TestCase):
    def test_node_script_generates_html(self) -> None:
        payload = load_json(ROOT / "data" / "sample_open_meteo.json")
        daily = aggregate_daily(payload)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            json_path, _ = write_outputs(
                daily,
                out,
                location_name="宝塚市",
                latitude=34.799,
                longitude=135.356,
                source="test-fixture",
            )
            html_path = out / "index.html"
            subprocess.run(
                ["node", str(ROOT / "tools" / "generate_dashboard.js"), str(json_path), str(html_path)],
                check=True,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("HW25A066", html)
            self.assertIn("出力データ一覧", html)
            self.assertIn("宝塚市", html)


if __name__ == "__main__":
    unittest.main()
