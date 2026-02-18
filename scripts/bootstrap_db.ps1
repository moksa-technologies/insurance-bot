param(
  [string]$HostName = $env:POSTGRES_HOST,
  [string]$Port = $env:POSTGRES_PORT,
  [string]$Database = $env:POSTGRES_DB,
  [string]$User = $env:POSTGRES_USER,
  [switch]$Seed
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

$schemaRoot = Join-Path $PSScriptRoot "..\..\Database_schema"
if (Test-Path (Join-Path $schemaRoot "Insurence_Db")) {
  $schemaRoot = Join-Path $schemaRoot "Insurence_Db"
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

function Ensure-DatabaseExists {
  param(
    [string]$DbHost,
    [string]$DbPort,
    [string]$DbName,
    [string]$DbUser
  )

  $checkSql = "SELECT 1 FROM pg_database WHERE datname = '$DbName';"
  $exists = psql -h $DbHost -p $DbPort -U $DbUser -d postgres -t -A -c $checkSql
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to check database existence for '$DbName'."
  }

  if ($exists.Trim() -eq "1") {
    return
  }

  Write-Host "Database '$DbName' not found. Creating..." -ForegroundColor Yellow
  psql -h $DbHost -p $DbPort -U $DbUser -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE `"$DbName`";"
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to create database '$DbName'."
  }
}

function Test-SchemaExists {
  param(
    [string]$DbHost,
    [string]$DbPort,
    [string]$DbName,
    [string]$DbUser
  )

  $sql = "SELECT to_regclass('public.customer') IS NOT NULL;"
  $exists = psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -t -A -c $sql
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to check schema existence in database '$DbName'."
  }
  return ($exists.Trim().ToLower() -eq "t")
}

$files = @(
  (Join-Path $schemaRoot "Tables\insurancedb_schema.sql"),
  (Join-Path $schemaRoot "Functions\customer_create.sql"),
  (Join-Path $schemaRoot "Functions\get_customer_profile_by_ani.sql"),
  (Join-Path $schemaRoot "Functions\update_customer_email_by_ani.sql"),
  (Join-Path $schemaRoot "Functions\update_customer_address_by_ani.sql"),
  (Join-Path $schemaRoot "Functions\change_customer_ani.sql"),
  (Join-Path $schemaRoot "Functions\create_claim_by_ani.sql"),
  (Join-Path $schemaRoot "Functions\CALL_BACK_CRUD.sql")
)

if ($Seed.IsPresent) {
  $files += (Join-Path $schemaRoot "dummy_data\seeddummydata.sql")
}

Ensure-DatabaseExists -DbHost $HostName -DbPort $Port -DbName $Database -DbUser $User
$schemaExists = Test-SchemaExists -DbHost $HostName -DbPort $Port -DbName $Database -DbUser $User

foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    Write-Host "Missing SQL file: $file" -ForegroundColor Red
    exit 1
  }
  if ((Split-Path $file -Leaf) -eq "insurancedb_schema.sql" -and $schemaExists) {
    Write-Host "Skipping $file (schema already exists)." -ForegroundColor Yellow
    continue
  }
  Write-Host "Applying $file..." -ForegroundColor Cyan
  psql -h $HostName -p $Port -U $User -d $Database -v ON_ERROR_STOP=1 -f $file
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed applying $file" -ForegroundColor Red
    exit $LASTEXITCODE
  }
}

Write-Host "Database bootstrap completed." -ForegroundColor Green
