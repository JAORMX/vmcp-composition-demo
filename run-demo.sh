#!/bin/bash
#
# Convenience script to run the Virtual MCP Composition Demo
# Automatically activates venv and runs the demo
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if vmcp binary exists
if [ ! -f "../../bin/vmcp" ]; then
    echo "Error: vmcp binary not found"
    echo "Please run: task build-vmcp"
    exit 1
fi

# Activate venv and run demo
source .venv/bin/activate
exec python3 demo.py "$@"
