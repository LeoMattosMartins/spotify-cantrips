#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_PID=""
HUD_PID=""

cleanup() {
  if [[ -n "${HUD_PID}" ]] && kill -0 "${HUD_PID}" 2>/dev/null; then
    kill "${HUD_PID}" 2>/dev/null || true
  fi
  if [[ -n "${ENGINE_PID}" ]] && kill -0 "${ENGINE_PID}" 2>/dev/null; then
    kill "${ENGINE_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

if [[ ! -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  echo "Missing Python virtualenv at .venv. Run setup steps in README first."
  exit 1
fi

if [[ ! -d "${ROOT_DIR}/hud/node_modules" ]]; then
  echo "Missing HUD dependencies. Run: (cd hud && npm install)"
  exit 1
fi

source "${ROOT_DIR}/.venv/bin/activate"

python "${ROOT_DIR}/engine/main.py" &
ENGINE_PID=$!

(
  cd "${ROOT_DIR}/hud"
  npm start
) &
HUD_PID=$!

while true; do
  if ! kill -0 "${ENGINE_PID}" 2>/dev/null; then
    break
  fi
  if ! kill -0 "${HUD_PID}" 2>/dev/null; then
    break
  fi
  sleep 1
done
