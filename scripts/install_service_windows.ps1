param(
  [string]$ServiceName = "InsurenceBot",
  [string]$DisplayName = "Insurence Bot Service",
  [string]$Description = "Insurence Bot FastAPI service",
  [string]$PythonExe = "",
  [string]$VenvDir = ".venv",
  [string]$HostName = "0.0.0.0",
  [int]$Port = 8000,
  [int]$Workers = 1,
  [string]$NssmPath = "",
  [switch]$SkipSetup,
  [switch]$SkipBootstrap,
  [switch]$SkipVerify,
  [switch]$Seed,
  [switch]$ForceReinstall,
  [switch]$NoStart,
  [switch]$Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
  @"
Usage: install_service_windows.ps1 [options]

Options:
  -ServiceName <name>      Windows service name (default: InsurenceBot)
  -DisplayName <name>      Windows service display name
  -Description <text>      Service description
  -PythonExe <exe>         Python executable for virtualenv setup
  -VenvDir <path>          Virtualenv directory (default: .venv)
  -HostName <host>         Uvicorn host (default: 0.0.0.0)
  -Port <port>             Uvicorn port (default: 8000)
  -Workers <num>           Uvicorn workers (default: 1)
  -NssmPath <path>         Explicit path to nssm.exe
  -SkipSetup               Skip deploy/setup step
  -SkipBootstrap           Skip DB bootstrap during setup
  -SkipVerify              Skip DB verify during setup
  -Seed                    Run DB bootstrap with seed
  -ForceReinstall          Remove existing service and reinstall
  -NoStart                 Install service but do not start
"@ | Write-Host
  exit 0
}

function Test-IsAdmin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p = New-Object Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Resolve-NssmExe([string]$candidate) {
  if ($candidate -and (Test-Path $candidate)) { return (Resolve-Path $candidate).Path }

  $cmd = Get-Command nssm.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  $common = @(
    "C:\Program Files\nssm\win64\nssm.exe",
    "C:\Program Files\nssm\win32\nssm.exe",
    "C:\nssm\win64\nssm.exe",
    "C:\nssm\win32\nssm.exe"
  )
  foreach ($path in $common) {
    if (Test-Path $path) { return $path }
  }
  throw "nssm.exe not found. Install NSSM and provide -NssmPath."
}

function Invoke-Nssm {
  param(
    [string]$Exe,
    [string[]]$Args
  )

  & $Exe @Args | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "NSSM command failed: $Exe $($Args -join ' ')"
  }
}

if (-not (Test-IsAdmin)) {
  throw "Run this script as Administrator."
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot
$nssmExe = Resolve-NssmExe $NssmPath

Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host "Using NSSM: $nssmExe" -ForegroundColor Cyan

if (-not $SkipSetup) {
  $deployArgs = @(
    "-VenvDir", $VenvDir,
    "-HostName", $HostName,
    "-Port", $Port,
    "-Workers", $Workers,
    "-NoStart"
  )
  if ($PythonExe) { $deployArgs += @("-PythonExe", $PythonExe) }
  if ($SkipBootstrap) { $deployArgs += "-SkipBootstrap" }
  if ($SkipVerify) { $deployArgs += "-SkipVerify" }
  if ($Seed) { $deployArgs += "-Seed" }
  & (Join-Path $PSScriptRoot "deploy_windows.ps1") @deployArgs
}

$venvPath = Join-Path $projectRoot $VenvDir
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Virtual environment python not found: $venvPython"
}

$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService -and -not $ForceReinstall) {
  throw "Service '$ServiceName' already exists. Use -ForceReinstall to replace."
}

if ($existingService -and $ForceReinstall) {
  Invoke-Nssm -Exe $nssmExe -Args @("stop", $ServiceName)
  Invoke-Nssm -Exe $nssmExe -Args @("remove", $ServiceName, "confirm")
  Start-Sleep -Seconds 1
}

New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "logs") | Out-Null

$appArgs = "-m uvicorn app.main:app --host $HostName --port $Port --workers $Workers"
$stdoutLog = Join-Path $projectRoot "logs\$ServiceName.out.log"
$stderrLog = Join-Path $projectRoot "logs\$ServiceName.err.log"
Invoke-Nssm -Exe $nssmExe -Args @("install", $ServiceName, $venvPython, $appArgs)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "DisplayName", $DisplayName)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "Description", $Description)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppDirectory", $projectRoot)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "Start", "SERVICE_AUTO_START")
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppStdout", $stdoutLog)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppStderr", $stderrLog)
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppRotateFiles", "1")
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppRotateOnline", "1")
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppRotateSeconds", "86400")
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppEnvironmentExtra", "PYTHONUNBUFFERED=1`nPYTHONDONTWRITEBYTECODE=1")
Invoke-Nssm -Exe $nssmExe -Args @("set", $ServiceName, "AppExit", "Default", "Restart")

if (-not $NoStart) {
  Invoke-Nssm -Exe $nssmExe -Args @("start", $ServiceName)
}

Get-Service -Name $ServiceName | Format-Table -AutoSize
Write-Host "Service installed: $ServiceName" -ForegroundColor Green
