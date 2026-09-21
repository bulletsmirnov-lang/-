#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN is not set (add it to .env or export it)}"
: "${TELEGRAM_CHAT_ID:?TELEGRAM_CHAT_ID is not set (add it to .env or export it)}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"message text\"" >&2
  exit 1
fi

message="$1"

response=$(curl -sS -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${message}")

if command -v jq &>/dev/null; then
  echo "$response" | jq .
else
  echo "$response"
fi

echo "$response" | grep -q '"ok":true'
