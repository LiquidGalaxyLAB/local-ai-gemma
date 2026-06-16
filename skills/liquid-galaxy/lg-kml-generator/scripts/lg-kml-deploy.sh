#!/bin/bash
# lg-kml-deploy.sh
# Simple script to deploy KML files to Liquid Galaxy master node (lg1)

set -euo pipefail

# Configuration
LG_USERNAME="${LG_USERNAME:-lg}"
LG_PASSWORD="${LG_PASSWORD:-lg}"
LG_HOST="${LG_HOST:-localhost}"
LG_PORT="${LG_PORT:-2222}"
KML_DIR="/var/www/html/kmls"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"

# Display usage
usage() {
    echo "Usage: $0 -f <kml_file> [-n <remote_name>] [-r] [-h]"
    echo "  -f <kml_file>   Local KML file to deploy"
    echo "  -n <name>       Remote filename (defaults to local filename)"
    echo "  -r              Trigger relaunch after deployment"
    echo "  -h              Show this help message"
    exit 1
}

# Parse arguments
REMOTE_NAME=""
TRIGGER_RELAUNCH=false

while getopts ":f:n:rh" opt; do
    case $opt in
        f) KML_FILE="$OPTARG" ;;
        n) REMOTE_NAME="$OPTARG" ;;
        r) TRIGGER_RELAUNCH=true ;;
        h) usage ;;
        \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
        :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
    esac
done

# Validate required arguments
if [[ -z "${KML_FILE:-}" ]]; then
    echo "Error: KML file (-f) is required" >&2
    usage
fi

if [[ ! -f "$KML_FILE" ]]; then
    echo "Error: KML file '$KML_FILE' not found" >&2
    exit 1
fi

# Check for required tools
command -v sshpass >/dev/null 2>&1 || { echo "Error: sshpass not found. Install with: sudo apt install sshpass"; exit 1; }

# Set remote filename
if [[ -z "$REMOTE_NAME" ]]; then
    REMOTE_NAME="$(basename "$KML_FILE")"
fi

# Validate LG password
if [[ -z "$LG_PASSWORD" ]]; then
    echo "Error: LG_PASSWORD is empty" >&2
    exit 1
fi

echo "Deploying KML file: $KML_FILE"
echo "Target: $LG_USERNAME@$LG_HOST:$LG_PORT $KML_DIR/$REMOTE_NAME"

# Validate KML syntax if xmllint is available
if command -v xmllint >/dev/null 2>&1; then
    echo "Validating KML syntax..."
    if ! xmllint --noout "$KML_FILE" >/dev/null 2>&1; then
        echo "Error: KML syntax validation failed" >&2
        exit 1
    fi
    echo "✓ KML syntax is valid"
fi

# Deploy the file
echo "Deploying to Liquid Galaxy..."
sshpass -p "$LG_PASSWORD" scp $SSH_OPTS -P "$LG_PORT" "$KML_FILE" "${LG_USERNAME}@${LG_HOST}:${KML_DIR}/${REMOTE_NAME}"

# Verify deployment
echo "Verifying deployment..."
if sshpass -p "$LG_PASSWORD" ssh $SSH_OPTS -p "$LG_PORT" "${LG_USERNAME}@${LG_HOST}" "[[ -f \"$KML_DIR/$REMOTE_NAME\" ]]"; then
    echo "✓ File deployed successfully"
else
    echo "Error: File deployment verification failed" >&2
    exit 1
fi

# Show file info
echo "File information:"
sshpass -p "$LG_PASSWORD" ssh $SSH_OPTS -p "$LG_PORT" "${LG_USERNAME}@${LG_HOST}" "ls -la \"$KML_DIR/$REMOTE_NAME\""

# Trigger relaunch if requested
if $TRIGGER_RELAUNCH; then
    echo "Triggering LG relaunch..."
    sshpass -p "$LG_PASSWORD" ssh $SSH_OPTS -p "$LG_PORT" "${LG_USERNAME}@${LG_HOST}" "/home/lg/bin/lg-relaunch-direct"
    echo "✓ Relaunch triggered"
fi

echo "Deployment complete!"