param(
    [Parameter(Mandatory=$true)][string]$VideoPath,
    [Parameter(Mandatory=$true)][string]$JenkinsLogPath
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root "HW25A066_提出用"
$Zip = Join-Path $Root "HW25A066_スクリプトプログラミング演習2_提出.zip"

if (!(Test-Path $VideoPath)) { throw "動画が見つかりません: $VideoPath" }
if (!(Test-Path $JenkinsLogPath)) { throw "Jenkinsログが見つかりません: $JenkinsLogPath" }
$logText = Get-Content $JenkinsLogPath -Raw
if ($logText -notmatch "Finished: SUCCESS") { throw "Jenkinsログに Finished: SUCCESS がありません" }

Remove-Item $Out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $Out | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Out "project") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Out "output") | Out-Null

$projectItems = @("Jenkinsfile", "README.md", "fetch_weather.py", "run_local.py", "src", "tools", "tests", "data")
foreach ($item in $projectItems) {
    Copy-Item (Join-Path $Root $item) (Join-Path $Out "project") -Recurse -Force
}
Copy-Item (Join-Path $Root "output\weather_data.json") (Join-Path $Out "output") -Force
Copy-Item (Join-Path $Root "output\weather_data.csv") (Join-Path $Out "output") -Force
Copy-Item (Join-Path $Root "output\index.html") (Join-Path $Out "output") -Force
Copy-Item (Join-Path $Root "output\build_summary.json") (Join-Path $Out "output") -Force
Copy-Item $VideoPath (Join-Path $Out "jenkins実行動画_HW25A066.mp4") -Force
Copy-Item $JenkinsLogPath (Join-Path $Out "jenkins_console_HW25A066.txt") -Force
if (Test-Path (Join-Path $Root "HW25A066_最終レポート.pdf")) {
    Copy-Item (Join-Path $Root "HW25A066_最終レポート.pdf") $Out -Force
}

Remove-Item $Zip -Force -ErrorAction SilentlyContinue
Compress-Archive -Path "$Out\*" -DestinationPath $Zip -CompressionLevel Optimal
Write-Host "提出ZIPを作成しました: $Zip"
