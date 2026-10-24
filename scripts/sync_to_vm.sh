#!/usr/bin/env bash
# Copy the current working tree (tracked + untracked, not ignored files) to the
# test VM so uncommitted work can be built and run there.
#
#   scripts/sync_to_vm.sh [ssh-host] [remote-dir]
#
# Defaults: host "serabot-vm" (see docs/DEV_ENVIRONMENT.md), dir "serabot_ws".
# The remote copy is not a git clone; src/, docker/ and scripts/ are replaced on
# every sync, colcon's build/, install/ and log/ are kept.
set -euo pipefail

HOST="${1:-serabot-vm}"
DEST="${2:-serabot_ws}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT"
git ls-files -z --cached --others --exclude-standard \
    | tar --null --ignore-failed-read -cf - -T - 2>/dev/null \
    | ssh "$HOST" "mkdir -p '$DEST' && cd '$DEST' && rm -rf src docker scripts && tar -xf - && chmod +x docker/*.sh scripts/*.sh"

echo "Synced $REPO_ROOT -> $HOST:~/$DEST"
