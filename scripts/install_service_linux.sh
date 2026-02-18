#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root (use sudo)." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVICE_NAME="${SERVICE_NAME:-insurence-bot}"
SERVICE_USER="${SERVICE_USER:-${SUDO_USER:-root}}"
SERVICE_GROUP="${SERVICE_GROUP:-${SERVICE_USER}}"
PYTHON_BIN="${PYTHON_BIN:-}"
VENV_DIR="${VENV_DIR:-${PROJECT_ROOT}/.venv}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
SKIP_SETUP="false"
SKIP_BOOTSTRAP="false"
SKIP_VERIFY="false"
SEED="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      cat <<'USAGE'
Usage: install_service_linux.sh [options]

Options:
  --service-name <name>   systemd service name (default: insurence-bot)
  --service-user <user>   user for service process
  --service-group <group> group for service process
  --python <python_bin>   python executable for venv creation
  --venv <path>           virtualenv path
  --host <host>           uvicorn host (default: 0.0.0.0)
  --port <port>           uvicorn port (default: 8000)
  --workers <num>         uvicorn workers (default: 1)
  --skip-setup            skip deploy/setup step
  --skip-bootstrap        skip DB bootstrap during setup
  --skip-verify           skip DB verification during setup
  --seed                  run DB bootstrap with seed
USAGE
      exit 0
      ;;
    --service-name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --service-user)
      SERVICE_USER="$2"
      shift 2
      ;;
    --service-group)
      SERVICE_GROUP="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
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
    --skip-setup)
      SKIP_SETUP="true"
      shift
      ;;
    --skip-bootstrap)
      SKIP_BOOTSTRAP="true"
      shift
      ;;
    --skip-verify)
      SKIP_VERIFY="true"
      shift
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

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found. This installer requires systemd." >&2
  exit 1
fi

if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
  echo "Service user not found: ${SERVICE_USER}" >&2
  exit 1
fi

UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_PYTHON="${VENV_DIR}/bin/python"
WRAPPER_PATH="/usr/local/bin/${SERVICE_NAME}.sh"

echo "Installing Linux service '${SERVICE_NAME}'..."
echo "Project root: ${PROJECT_ROOT}"

if [[ "${SKIP_SETUP}" != "true" ]]; then
  DEPLOY_ARGS=(--venv "${VENV_DIR}" --host "${HOST}" --port "${PORT}" --workers "${WORKERS}" --no-start)
  if [[ -n "${PYTHON_BIN}" ]]; then
    DEPLOY_ARGS+=(--python "${PYTHON_BIN}")
  fi
  if [[ "${SKIP_BOOTSTRAP}" == "true" ]]; then
    DEPLOY_ARGS+=(--skip-bootstrap)
  fi
  if [[ "${SKIP_VERIFY}" == "true" ]]; then
    DEPLOY_ARGS+=(--skip-verify)
  fi
  if [[ "${SEED}" == "true" ]]; then
    DEPLOY_ARGS+=(--seed)
  fi
  chmod +x "${SCRIPT_DIR}/deploy_linux.sh"
  "${SCRIPT_DIR}/deploy_linux.sh" "${DEPLOY_ARGS[@]}"
fi

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "Virtualenv python not found: ${VENV_PYTHON}" >&2
  exit 1
fi

mkdir -p "${PROJECT_ROOT}/logs"
chown -R "${SERVICE_USER}:${SERVICE_GROUP}" "${PROJECT_ROOT}/logs" || true

cat > "${WRAPPER_PATH}" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
cd '${PROJECT_ROOT}'
exec '${VENV_PYTHON}' -m uvicorn app.main:app --host '${HOST}' --port '${PORT}' --workers '${WORKERS}'
EOF
chmod 755 "${WRAPPER_PATH}"

cat > "${UNIT_PATH}" <<EOF
[Unit]
Description=Insurence Bot FastAPI Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
Environment=PYTHONUNBUFFERED=1
ExecStart=${WRAPPER_PATH}
Restart=always
RestartSec=5
TimeoutStopSec=30
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}"
systemctl --no-pager --full status "${SERVICE_NAME}" || true

echo "Service installed: ${SERVICE_NAME}"
echo "Use: sudo systemctl status ${SERVICE_NAME}"
