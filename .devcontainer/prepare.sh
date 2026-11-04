#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
mkdir -p outputs/codespaces
if [[ ! -s outputs/codespaces/session.env ]]; then
  demo_secret=$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')
  printf 'DEMO_SESSION_SECRET=%s\n' "$demo_secret" > outputs/codespaces/session.env
fi
printf '%s\n' 'MirrorCheck is prepared. No paid service was created.'
printf '%s\n' 'Check the remaining Codespaces allowance and a $0 budget with Stop usage enabled.'
printf '%s\n' 'Add META_API_KEY as a Codespaces secret for this repository, then run: bash .devcontainer/start.sh'
