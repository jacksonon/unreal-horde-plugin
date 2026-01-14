param(
  [switch]$SkipInject
)

$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Resolve-Path (Join-Path $ToolsDir "..")
$ProjectRoot = Resolve-Path (Join-Path $BuildRoot "..")

$ConfigPath = Join-Path $ProjectRoot "Config/BuildSystem/BuildConfig.json"
$TemplatePath = Join-Path $BuildRoot "Templates/BuildConfig.template.json"

Write-Host "[info] ProjectRoot: $ProjectRoot"
Write-Host "[info] BuildRoot:   $BuildRoot"
Write-Host "[info] ConfigPath:  $ConfigPath"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "[error] Python not found. Install Python 3.x and ensure python is in PATH."
  exit 1
}

if (-not (Test-Path $ConfigPath)) {
  Write-Host "[info] Creating default config from template..."
  New-Item -ItemType Directory -Force (Split-Path -Parent $ConfigPath) | Out-Null
  Copy-Item -Force $TemplatePath $ConfigPath
  Write-Host "[next] Please edit: $ConfigPath"
}

if (-not $SkipInject) {
  Write-Host "[info] Injecting UBT BuildConfiguration.xml (UBA coordinator)..."
  python (Join-Path $BuildRoot "Scripts/Inject_Global_Config.py") --config-path $ConfigPath
}

Write-Host "[info] Running doctor..."
python (Join-Path $BuildRoot "Tools/uebuild.py") --config-path $ConfigPath doctor

Write-Host "[ok] Environment ready."
