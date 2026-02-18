param(
  [string]$PythonExe = "",
  [string]$VenvDir = ".venv",
  [string]$HostName = "0.0.0.0",
  [int]$Port = 8000,
  [int]$Workers = 1,
  [switch]$SkipBootstrap,
  [switch]$SkipVerify,
  [switch]$NoStart,
  [switch]$Seed,
  [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"

function Resolve-PythonExe([string]$candidate) {
  if ($candidate) {
    if (Test-Path $candidate) {
      return (Resolve-Path $candidate).Path
    }
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
      return $cmd.Source
    }
    throw "Python executable not found: $candidate"
  }

  $defaults = @("python3.13", "python3.12", "python3.11", "python")
  foreach ($name in $defaults) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
      return $cmd.Source
    }
  }

  throw "No Python executable found. Install Python 3.11+ and rerun."
}

function Get-PythonVersion([string]$exePath) {
  $verText = & $exePath -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
  return [Version]$verText.Trim()
}

function Assert-PythonSupported([string]$exePath) {
  $ver = Get-PythonVersion $exePath
  if ($ver.Major -lt 3 -or ($ver.Major -eq 3 -and $ver.Minor -lt 11)) {
    throw "Unsupported Python version $ver at '$exePath'. This project requires Python 3.11+."
  }
  return $ver
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

$resolvedPython = Resolve-PythonExe $PythonExe
$resolvedVersion = Assert-PythonSupported $resolvedPython
Write-Host "Using Python: $resolvedPython ($resolvedVersion)" -ForegroundColor Cyan

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example (update secrets before production use)." -ForegroundColor Yellow
}

$venvPath = Join-Path $projectRoot $VenvDir
if ((Test-Path $venvPath) -and $RecreateVenv) {
  Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath)) {
  & $resolvedPython -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Virtual environment python not found: $venvPython"
}

$venvVersion = Get-PythonVersion $venvPython
if ($venvVersion.Major -lt 3 -or ($venvVersion.Major -eq 3 -and $venvVersion.Minor -lt 11)) {
  throw "Existing virtualenv uses unsupported Python $venvVersion. Re-run with -RecreateVenv."
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

if (-not $SkipBootstrap) {
  if ($Seed) {
    & (Join-Path $PSScriptRoot "bootstrap_db.ps1") -Seed
  } else {
    & (Join-Path $PSScriptRoot "bootstrap_db.ps1")
  }
}

if (-not $SkipVerify) {
  & (Join-Path $PSScriptRoot "verify_db.ps1")
}

if (-not $NoStart) {
  Write-Host "Starting app on ${HostName}:${Port} with ${Workers} worker(s)..." -ForegroundColor Green
  & $venvPython -m uvicorn app.main:app --host $HostName --port $Port --workers $Workers
}

Write-Host "Deployment steps completed." -ForegroundColor Green
