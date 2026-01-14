$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Resolve-Path (Join-Path $ToolsDir "..")
$ProjectRoot = Resolve-Path (Join-Path $BuildRoot "..")

$Src = Join-Path $BuildRoot "Extras/UEBuildSDKPlugin/UEBuildSDK"
$Dst = Join-Path $ProjectRoot "Plugins/UEBuildSDK"

if (-not (Test-Path $Src)) {
  Write-Host "[error] Plugin source not found: $Src"
  exit 1
}

New-Item -ItemType Directory -Force $Dst | Out-Null

Write-Host "[info] Copying plugin to: $Dst"
Copy-Item -Recurse -Force (Join-Path $Src "*") $Dst

Write-Host "[ok] Installed. Enable plugin in Editor: Plugins -> UE Build SDK"

