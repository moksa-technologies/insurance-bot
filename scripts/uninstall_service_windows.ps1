param(
  [string]$ServiceName = "InsurenceBot",
  [string]$NssmPath = "",
  [switch]$RemoveLogs,
  [switch]$Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
  @"
Usage: uninstall_service_windows.ps1 [options]

Options:
  -ServiceName <name>   Windows service name to remove
  -NssmPath <path>      Explicit nssm.exe path
  -RemoveLogs           Remove service stdout/stderr logs in .\logs
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
$nssmExe = Resolve-NssmExe $NssmPath

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $service) {
  Write-Host "Service '$ServiceName' not found." -ForegroundColor Yellow
  return
}

Invoke-Nssm -Exe $nssmExe -Args @("stop", $ServiceName)
Invoke-Nssm -Exe $nssmExe -Args @("remove", $ServiceName, "confirm")

if ($RemoveLogs) {
  $stdoutLog = Join-Path $projectRoot "logs\$ServiceName.out.log"
  $stderrLog = Join-Path $projectRoot "logs\$ServiceName.err.log"
  Remove-Item -Force -ErrorAction SilentlyContinue `
    $stdoutLog, `
    $stderrLog
}

Write-Host "Service uninstalled: $ServiceName" -ForegroundColor Green
