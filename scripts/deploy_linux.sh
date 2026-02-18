#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-}"
VENV_DIR="${VENV_DIR:-${PROJECT_ROOT}/.venv}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
RUN_BOOTSTRAP="true"
RUN_VERIFY="true"
START_APP="true"
SEED="false"
RECREATE_VENV="false"
PYTHON_EXPLICIT="false"

resolve_python_bin() {
  if [[ "${PYTHON_EXPLICIT}" == "true" ]]; then
    if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
      echo "Python executable not found: ${PYTHON_BIN}" >&2
      exit 1
    fi
    return
  fi

  local candidate
  for candidate in python3.13 python3.12 python3.11 python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      PYTHON_BIN="${candidate}"
      return
    fi
  done

  echo "No Python executable found. Install Python 3.11+ and rerun." >&2
  exit 1
}

python_version_string() {
  local exe="$1"
  "${exe}" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
PY
}

python_is_compatible() {
  local exe="$1"
  "${exe}" - <<'PY'
import sys
sys.exit(0 if (sys.version_info.major, sys.version_info.minor) >= (3, 11) else 1)
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      cat <<'USAGE'
Usage: deploy_linux.sh [options]

Options:
  --python <bin>        Python executable (must be 3.11+)
  --venv <path>         Virtualenv path (default: ./.venv)
  --host <host>         Uvicorn host (default: 0.0.0.0)
  --port <port>         Uvicorn port (default: 8000)
  --workers <num>       Uvicorn workers (default: 1)
  --skip-bootstrap      Skip DB bootstrap
  --skip-verify         Skip DB function verification
  --no-start            Do not start uvicorn
  --seed                Run DB bootstrap with seed data
  --recreate-venv       Recreate venv if it already exists
USAGE
      exit 0
      ;;
    --python)
      PYTHON_BIN="$2"
      PYTHON_EXPLICIT="true"
      shift 2
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --workers)
      WORKERS="$2"
      shift 2
      ;;
    --skip-bootstrap)
      RUN_BOOTSTRAP="false"
      shift
      ;;
    --skip-verify)
      RUN_VERIFY="false"
      shift
      ;;
    --no-start)
      START_APP="false"
      shift
      ;;
    --seed)
      SEED="true"
      shift
      ;;
    --recreate-venv)
      RECREATE_VENV="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

resolve_python_bin

if ! python_is_compatible "${PYTHON_BIN}"; then
  echo "Python ${PYTHON_BIN} is not supported: $(python_version_string "${PYTHON_BIN}")" >&2
  echo "This project requires Python 3.11+." >&2
  exit 1
fi

echo "Project root: ${PROJECT_ROOT}"
echo "Using Python: ${PYTHON_BIN} ($(python_version_string "${PYTHON_BIN}"))"
cd "${PROJECT_ROOT}"

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp ".env.example" ".env"
  echo "Created .env from .env.example (update secrets before production use)."
fi

if [[ -d "${VENV_DIR}" && "${RECREATE_VENV}" == "true" ]]; then
  rm -rf "${VENV_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "Virtualenv Python not found at ${VENV_DIR}/bin/python" >&2
  exit 1
fi

if ! python_is_compatible "${VENV_DIR}/bin/python"; then
  echo "Existing virtualenv uses unsupported Python: $(python_version_string "${VENV_DIR}/bin/python")" >&2
  echo "Run again with --recreate-venv (or delete ${VENV_DIR}) to rebuild with Python 3.11+." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ "${RUN_BOOTSTRAP}" == "true" ]]; then
  chmod +x "${SCRIPT_DIR}/bootstrap_db.sh"
  if [[ "${SEED}" == "true" ]]; then
    "${SCRIPT_DIR}/bootstrap_db.sh" --seed
  else
    "${SCRIPT_DIR}/bootstrap_db.sh"
  fi
fi

if [[ "${RUN_VERIFY}" == "true" ]]; then
  chmod +x "${SCRIPT_DIR}/verify_db.sh"
  "${SCRIPT_DIR}/verify_db.sh"
fi

if [[ "${START_APP}" == "true" ]]; then
  echo "Starting app on ${HOST}:${PORT} with ${WORKERS} worker(s)..."
  exec python -m uvicorn app.main:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
fi

echo "Deployment steps completed."
