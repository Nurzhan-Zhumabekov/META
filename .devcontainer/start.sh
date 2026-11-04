#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${META_API_KEY:-}" ]]; then
  printf '%s\n' 'META_API_KEY is missing. Add it under GitHub Settings > Codespaces > Secrets for this repository.' >&2
  printf '%s\n' 'Do not paste the key into source files, terminal commands or chat. Restart the codespace after adding the secret.' >&2
  exit 1
fi
bash .devcontainer/prepare.sh
docker compose --env-file outputs/codespaces/session.env -f compose.demo.yaml up -d --build
for ((attempt=0; attempt<180; attempt++)); do
  if curl --fail --silent http://127.0.0.1:8090/healthz >/dev/null; then
    printf '%s\n' 'Ready: http://localhost:8090/demo-guide.html'
    printf '%s\n' 'In the Ports panel, make only port 8090 Public after verifying this isolated demo.'
    printf '%s\n' 'Keep OCR/privacy ports private. Stop the codespace when the demonstration ends.'
    exit 0
  fi
  sleep 1
done
printf '%s\n' 'Readiness failed. Inspect docker compose logs; do not expose an unhealthy service.' >&2
exit 1
