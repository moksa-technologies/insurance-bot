#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

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
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

db_exists="$(psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "postgres" -t -A -c "SELECT 1 FROM pg_database WHERE datname='${DATABASE}';" | tr -d '[:space:]')"
if [[ "${db_exists}" != "1" ]]; then
  echo "Database not found: ${DATABASE} (host=${HOST_NAME}, port=${PORT}, user=${DB_USER})" >&2
  exit 1
fi

SIGNATURES=(
  "customer_create(bigint,character varying,character varying,character varying,text,date)"
  "get_customer_profile_by_ani(text)"
  "update_customer_email_by_ani(text,text)"
  "update_customer_address_by_ani(text,text)"
  "change_customer_ani(text,text)"
  "create_claim_by_ani(text,text,date,time without time zone,text,text,text,boolean,text)"
  "callback_create(bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying)"
  "callback_get(bigint)"
  "callback_queue(character varying,character varying,timestamp with time zone,integer,integer)"
  "callback_update_patch(bigint,bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying,integer,timestamp with time zone,text)"
  "callback_mark_attempt(bigint,character varying,text,timestamp with time zone)"
  "callback_delete(bigint)"
)

all_ok=1
for sig in "${SIGNATURES[@]}"; do
  sql="SELECT to_regprocedure('${sig}') IS NOT NULL AS ok;"
  result="$(psql -h "${HOST_NAME}" -p "${PORT}" -U "${DB_USER}" -d "${DATABASE}" -t -A -c "${sql}" | tr -d '[:space:]')"
  if [[ "${result,,}" != "t" ]]; then
    echo "Missing function: ${sig}" >&2
    all_ok=0
  else
    echo "OK: ${sig}"
  fi
done

if [[ "${all_ok}" -ne 1 ]]; then
  exit 1
fi

echo "All required functions verified."
