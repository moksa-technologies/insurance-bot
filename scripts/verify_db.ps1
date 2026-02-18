param(
  [string]$HostName = $env:POSTGRES_HOST,
  [string]$Port = $env:POSTGRES_PORT,
  [string]$Database = $env:POSTGRES_DB,
  [string]$User = $env:POSTGRES_USER
)

function Import-DotEnv([string]$DotEnvPath) {
  if (-not (Test-Path $DotEnvPath)) {
    return
  }

  foreach ($line in Get-Content $DotEnvPath) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) {
      continue
    }

    $eqIndex = $trimmed.IndexOf("=")
    if ($eqIndex -lt 1) {
      continue
    }

    $key = $trimmed.Substring(0, $eqIndex).Trim()
    $value = $trimmed.Substring($eqIndex + 1).Trim().Trim("'").Trim('"')
    Set-Item -Path ("Env:{0}" -f $key) -Value $value
  }
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Import-DotEnv (Join-Path $projectRoot ".env")

if (-not $HostName) { $HostName = $env:POSTGRES_HOST }
if (-not $Port) { $Port = $env:POSTGRES_PORT }
if (-not $Database) { $Database = $env:POSTGRES_DB }
if (-not $User) { $User = $env:POSTGRES_USER }

if (-not $HostName) { $HostName = "localhost" }
if (-not $Port) { $Port = "5432" }
if (-not $Database) { $Database = "demo_insurence" }
if (-not $User) { $User = "postgres" }

if (-not $env:PGPASSWORD -and $env:POSTGRES_PASSWORD) {
  $env:PGPASSWORD = $env:POSTGRES_PASSWORD
}

$exists = psql -h $HostName -p $Port -U $User -d postgres -t -A -c "SELECT 1 FROM pg_database WHERE datname='$Database';"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Database check failed for '$Database'." -ForegroundColor Red
  exit $LASTEXITCODE
}
if ($exists.Trim() -ne "1") {
  Write-Host "Database not found: $Database (host=$HostName, port=$Port, user=$User)" -ForegroundColor Red
  exit 1
}

$signatures = @(
  "customer_create(bigint,character varying,character varying,character varying,text,date)",
  "get_customer_profile_by_ani(text)",
  "update_customer_email_by_ani(text,text)",
  "update_customer_address_by_ani(text,text)",
  "change_customer_ani(text,text)",
  "create_claim_by_ani(text,text,date,time without time zone,text,text,text,boolean,text)",
  "callback_create(bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying)",
  "callback_get(bigint)",
  "callback_queue(character varying,character varying,timestamp with time zone,integer,integer)",
  "callback_update_patch(bigint,bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying,integer,timestamp with time zone,text)",
  "callback_mark_attempt(bigint,character varying,text,timestamp with time zone)",
  "callback_delete(bigint)"
)

$allOk = $true
foreach ($sig in $signatures) {
  $sql = "SELECT to_regprocedure('$sig') IS NOT NULL AS ok;"
  $result = psql -h $HostName -p $Port -U $User -d $Database -t -A -c $sql
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Verification query failed for $sig" -ForegroundColor Red
    exit $LASTEXITCODE
  }
  if (($result.Trim()).ToLower() -ne "t") {
    Write-Host "Missing function: $sig" -ForegroundColor Red
    $allOk = $false
  } else {
    Write-Host "OK: $sig" -ForegroundColor Green
  }
}

if (-not $allOk) {
  exit 1
}

Write-Host "All required functions verified." -ForegroundColor Green
