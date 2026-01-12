#!/bin/bash

# Quick launcher for Skye with keep-alive
SKYE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Launching Skye with keep-alive monitoring..."
echo "📍 Directory: $SKYE_DIR"
echo "🌐 URL: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both Skye and the monitor"
echo ""

cd "$SKYE_DIR"
python3 keep_alive.py