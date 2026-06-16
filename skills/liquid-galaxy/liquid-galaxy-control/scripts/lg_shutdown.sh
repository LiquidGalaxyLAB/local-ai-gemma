#!/bin/bash
# Liquid Galaxy Shutdown Script
# Usage: ./lg_shutdown.sh <password> <ip> <port>
# Powers off only the target node. For multi-frame, use lg-poweroff-direct on lg1.

LG_PASS=${1:-"lg"}
LG_IP=${2:-"localhost"}
LG_PORT=${3:-"2222"}

sshpass -p "$LG_PASS" ssh -o StrictHostKeyChecking=no -p "$LG_PORT" -t lg@"$LG_IP" "echo '$LG_PASS' | sudo -S poweroff"
