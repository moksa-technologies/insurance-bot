#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root (use sudo)." >&2
  exit 1
fi

SERVICE_NAME="${SERVICE_NAME:-insurence-bot}"
REMOVE_LOGS="false"
PROJECT_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      cat <<'USAGE'
Usage: uninstall_service_linux.sh [options]

Options:
  --service-name <name>  systemd service name (default: insurence-bot)
  --remove-logs          remove service log files from project logs directory
  --project-root <path>  project root used for log cleanup
USAGE
      exit 0
      ;;
    --service-name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --remove-logs)
      REMOVE_LOGS="true"
      shift
      ;;
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
WRAPPER_PATH="/usr/local/bin/${SERVICE_NAME}.sh"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found. This uninstaller requires systemd." >&2
  exit 1
fi

if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
  systemctl stop "${SERVICE_NAME}" || true
  systemctl disable "${SERVICE_NAME}" || true
fi

if [[ -f "${UNIT_PATH}" ]]; then
  rm -f "${UNIT_PATH}"
fi

if [[ -f "${WRAPPER_PATH}" ]]; then
  rm -f "${WRAPPER_PATH}"
fi

systemctl daemon-reload
systemctl reset-failed || true

if [[ "${REMOVE_LOGS}" == "true" && -n "${PROJECT_ROOT}" ]]; then
  rm -f "${PROJECT_ROOT}/logs/${SERVICE_NAME}.out.log" "${PROJECT_ROOT}/logs/${SERVICE_NAME}.err.log" || true
fi

echo "Service uninstalled: ${SERVICE_NAME}"
