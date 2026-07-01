#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const inputPath = process.argv[2] || path.join("output", "weather_data.json");
const outputPath = process.argv[3] || path.join("output", "index.html");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bar(value, min, max) {
  const span = Math.max(max - min, 1);
  return Math.max(2, Math.min(100, ((value - min) / span) * 100));
}

if (!fs.existsSync(inputPath)) {
  console.error(`[dashboard] input not found: ${inputPath}`);
  process.exit(1);
}

const documentData = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const rows = documentData.daily || [];
if (rows.length === 0) {
  console.error("[dashboard] daily weather rows are empty");
  process.exit(1);
}

const temps = rows.flatMap((row) => [row.temp_min_c, row.temp_max_c]);
const tempMin = Math.floor(Math.min(...temps) - 2);
const tempMax = Math.ceil(Math.max(...temps) + 2);
const metadata = documentData.metadata || {};

const cards = rows
  .map((row) => {
    const low = bar(row.temp_min_c, tempMin, tempMax);
    const high = bar(row.temp_max_c, tempMin, tempMax);
    return `
      <article class="day-card">
        <h2>${escapeHtml(row.date)}</h2>
        <p class="weather">${escapeHtml(row.weather)}</p>
        <div class="temperature-scale" aria-label="最低・最高気温">
          <span class="range" style="left:${low}%;width:${Math.max(high - low, 2)}%"></span>
        </div>
        <dl>
          <div><dt>最低 / 最高</dt><dd>${row.temp_min_c.toFixed(1)} / ${row.temp_max_c.toFixed(1)} ℃</dd></div>
          <div><dt>平均湿度</dt><dd>${row.humidity_avg_pct.toFixed(1)} %</dd></div>
          <div><dt>降水量</dt><dd>${row.precipitation_total_mm.toFixed(1)} mm</dd></div>
          <div><dt>最大降水確率</dt><dd>${row.precipitation_probability_max_pct.toFixed(0)} %</dd></div>
        </dl>
      </article>`;
  })
  .join("\n");

const tableRows = rows
  .map(
    (row) => `<tr>
      <td>${escapeHtml(row.date)}</td>
      <td>${escapeHtml(row.weather)}</td>
      <td>${row.temp_min_c.toFixed(1)}</td>
      <td>${row.temp_max_c.toFixed(1)}</td>
      <td>${row.humidity_avg_pct.toFixed(1)}</td>
      <td>${row.precipitation_total_mm.toFixed(1)}</td>
      <td>${row.precipitation_probability_max_pct.toFixed(0)}</td>
    </tr>`
  )
  .join("\n");

const html = `<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(metadata.location || "天気")} 7日間天気データ</title>
  <style>
    :root { font-family: "Noto Sans JP", "Yu Gothic", sans-serif; color: #20242a; background: #f4f6f8; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    header { background: #17324d; color: white; padding: 28px max(24px, calc((100vw - 1100px) / 2)); }
    header h1 { margin: 0 0 8px; font-size: clamp(1.5rem, 4vw, 2.25rem); }
    header p { margin: 4px 0; opacity: .9; }
    main { max-width: 1100px; margin: 0 auto; padding: 28px 20px 48px; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
    .day-card { background: white; border: 1px solid #dce2e8; border-radius: 8px; padding: 16px; box-shadow: 0 2px 6px rgba(0,0,0,.04); }
    .day-card h2 { margin: 0; font-size: 1.05rem; }
    .weather { margin: 6px 0 12px; font-weight: 700; color: #295d88; }
    .temperature-scale { position: relative; height: 8px; margin: 15px 0; border-radius: 99px; background: linear-gradient(90deg,#6db4e8,#f6d55c,#ed6a5a); }
    .temperature-scale .range { position: absolute; top: -3px; height: 14px; border: 2px solid #172a3a; background: rgba(255,255,255,.65); border-radius: 99px; }
    dl { margin: 0; }
    dl div { display: flex; justify-content: space-between; gap: 12px; padding: 5px 0; border-top: 1px solid #edf0f2; }
    dt { color: #5c6770; }
    dd { margin: 0; font-variant-numeric: tabular-nums; font-weight: 600; }
    section { margin-top: 28px; }
    table { width: 100%; border-collapse: collapse; background: white; font-size: .92rem; }
    caption { text-align: left; font-weight: 700; font-size: 1.15rem; margin-bottom: 8px; }
    th, td { padding: 9px 10px; border: 1px solid #d9dfe5; text-align: right; }
    th { background: #eaf0f5; }
    th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
    footer { max-width: 1100px; margin: 0 auto; padding: 0 20px 32px; color: #5c6770; font-size: .85rem; }
    @media (max-width: 700px) { .table-wrap { overflow-x: auto; } table { min-width: 780px; } }
  </style>
</head>
<body>
  <header>
    <h1>${escapeHtml(metadata.location || "指定地点")} 7日間天気データ</h1>
    <p>生成日時: ${escapeHtml(metadata.generated_at || "-")}</p>
    <p>データ元: ${escapeHtml(metadata.source || "-")}</p>
  </header>
  <main>
    <div class="cards">${cards}</div>
    <section class="table-wrap">
      <table>
        <caption>出力データ一覧</caption>
        <thead><tr><th>日付</th><th>天気</th><th>最低℃</th><th>最高℃</th><th>湿度%</th><th>降水量mm</th><th>降水確率%</th></tr></thead>
        <tbody>${tableRows}</tbody>
      </table>
    </section>
  </main>
  <footer>スクリプトプログラミング演習2 / HW25A066 嶋田一歩 / JavaScriptによる拡張出力</footer>
</body>
</html>`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html, "utf8");
console.log(`[dashboard] generated: ${outputPath}`);
console.log(`[dashboard] rows: ${rows.length}`);
