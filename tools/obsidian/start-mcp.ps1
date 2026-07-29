$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$server = Join-Path $PSScriptRoot "mcp_server.py"

Set-Location $projectRoot
$env:PYTHONUTF8 = "1"
& python $server
