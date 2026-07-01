$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python run_local.py --offline
Start-Process (Resolve-Path "output/index.html")
