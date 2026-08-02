#!/bin/bash
# Deploy lg-*-direct helpers to lg1
# Usage: bash deploy-lg-reboot-direct.sh
# Deploys: lg-reboot-direct, lg-relaunch-direct, lg-poweroff-direct
# Requires: sshpass installed, tunnel on :2222 or direct LAN access

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SSH_OPTS="-o StrictHostKeyChecking=no"

# Detect mode: tunnel or direct
if ss -tlnp 2>/dev/null | grep -q :2222; then
  SSH_TARGET="lg@localhost -p 2222"
  SCP_PORT="-P 2222"
  SCP_HOST="lg@localhost"
elif [ -n "$LG_MASTER_IP" ]; then
  SSH_TARGET="lg@$LG_MASTER_IP"
  SCP_PORT=""
  SCP_HOST="lg@$LG_MASTER_IP"
else
  echo "No tunnel detected. Set LG_MASTER_IP=<ip> for direct LAN or ensure tunnel on :2222"
  exit 1
fi

deploy() {
  local src="$1"
  local dest="/home/lg/bin/$(basename $1)"
  if [ ! -f "$src" ]; then
    echo "  SKIP: $src not found"
    return
  fi
  sshpass -p 'lg' scp $SCP_PORT $SSH_OPTS "$src" "$SCP_HOST:$dest"
  sshpass -p 'lg' ssh $SSH_OPTS $SSH_TARGET "chmod +x $dest && echo '  deployed: $dest'"
}

echo "Deploying helpers to lg1..."
deploy "$SCRIPT_DIR/lg-reboot-direct"
deploy "$SCRIPT_DIR/lg-relaunch-direct"
deploy "$SCRIPT_DIR/lg-poweroff-direct"
deploy "$SCRIPT_DIR/lg-slave-master-refresh-set"

echo "Done."
