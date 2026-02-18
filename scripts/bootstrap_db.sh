#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SCHEMA_ROOT="${SCRIPT_DIR}/../../Database_schema"
if [[ -d "${SCHEMA_ROOT}/Insurence_Db" ]]; then
  SCHEMA_ROOT="${SCHEMA_ROOT}/Insurence_Db"
fi

load_dotenv() {
  local env_file="$1"
  [[ -f "${env_file}" ]] || return 0
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    [[ -z "${line}" || "${line:0:1}" == "#" ]] && continue
    [[ "${line}" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || continue
    local key="${line%%=*}"
    local value="${line#*=}"
    if [[ "${value}" =~ ^\".*\"$ ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${value}" =~ ^\'.*\'$ ]]; then
      value="${value:1:${#value}-2}"
    fi
    export "${key}=${value}"
  done < "${env_file}"
}

load_dotenv "${PROJECT_ROOT}/.env"

HOST_NAME="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5432}"
DATABASE="${POSTGRES_DB:-demo_insurence}"
DB_USER="${POSTGRES_USER:-postgres}"
SEED="false"

if [[ -z "${PGPASSWORD:-}" && -n "${POSTGRES_PASSWORD:-}" ]]; then
  export PGPASSWORD="${POSTGRES_PASSWORD}"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST_NAME="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --db|--database)
      DATABASE="$2"
      shift 2
      ;;
    --user)
      DB_USER="$2"
      shift 2
      ;;
    --seed)
      SEED="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

ensure_database_exists() {
  local exists
  exists="$(psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "postgres" -t -A -c "SELECT 1 FROM pg_database WHERE datname='${DATABASE}';" | tr -d '[:space:]')"
  if [[ "${exists}" == "1" ]]; then
    return
  fi
  echo "Database '${DATABASE}' not found. Creating..."
  psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "postgres" -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${DATABASE}\";"
}

schema_already_exists() {
  local exists
  exists="$(psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "${DATABASE}" -t -A -c "SELECT to_regclass('public.customer') IS NOT NULL;" | tr -d '[:space:]')"
  [[ "${exists,,}" == "t" ]]
}

FILES=(
  "${SCHEMA_ROOT}/Tables/insurancedb_schema.sql"
  "${SCHEMA_ROOT}/Functions/customer_create.sql"
  "${SCHEMA_ROOT}/Functions/get_customer_profile_by_ani.sql"
  "${SCHEMA_ROOT}/Functions/update_customer_email_by_ani.sql"
  "${SCHEMA_ROOT}/Functions/update_customer_address_by_ani.sql"
  "${SCHEMA_ROOT}/Functions/change_customer_ani.sql"
  "${SCHEMA_ROOT}/Functions/create_claim_by_ani.sql"
  "${SCHEMA_ROOT}/Functions/CALL_BACK_CRUD.sql"
)

if [[ "${SEED}" == "true" ]]; then
  FILES+=("${SCHEMA_ROOT}/dummy_data/seeddummydata.sql")
fi

ensure_database_exists

for file in "${FILES[@]}"; do
  if [[ ! -f "${file}" ]]; then
    echo "Missing SQL file: ${file}" >&2
    exit 1
  fi
  if [[ "$(basename "${file}")" == "insurancedb_schema.sql" ]] && schema_already_exists; then
    echo "Skipping ${file} (schema already exists)."
    continue
  fi
  echo "Applying ${file}..."
  psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "${DATABASE}" -v ON_ERROR_STOP=1 -f "${file}"
done

echo "Database bootstrap completed."
