#!/bin/bash
# Liquid Galaxy Relaunch Script
# Usage: ./lg_relaunch.sh <password> <ip> <port>
# Injects password to sudo -S so it works without interactive TTY.
# WARNING: Built-in lg-relaunch may silently fail if lg-ctl-master is missing.
#          This script bypasses that chain and calls service directly.

LG_PASS=${1:-"lg"}
LG_IP=${2:-"localhost"}
LG_PORT=${3:-"2222"}

RELAUNCH_CMD="if [ -f /etc/init/lxdm.conf ]; then SVC=lxdm; elif [ -f /etc/init/lightdm.conf ]; then SVC=lightdm; else exit 1; fi; echo '$LG_PASS' | sudo -S service \$SVC restart"

sshpass -p "$LG_PASS" ssh -o StrictHostKeyChecking=no -p "$LG_PORT" -t lg@"$LG_IP" "$RELAUNCH_CMD"
