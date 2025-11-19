#!/bin/bash
#
# Setup script for Virtual MCP Composition Demo
# Creates a virtual environment and installs dependencies
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Virtual MCP Composition Demo - Setup"
echo "=========================================="
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    echo "Please install Python 3.8 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "→ Found Python $PYTHON_VERSION"

# Create virtual environment
if [ -d ".venv" ]; then
    echo "→ Virtual environment already exists"
else
    echo "→ Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "→ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "→ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "→ Installing dependencies..."
pip install -r requirements.txt

echo
echo "✓ Setup complete!"
echo
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo
echo "1. Build Virtual MCP:"
echo "   cd ../.."
echo "   task build-vmcp"
echo
echo "2. Start backend MCP servers:"
echo "   thv run --name fetch --group default mcp/fetch --port 8090"
echo "   thv run --name github --group default mcp/github --port 8091"
echo "   thv run --name oci-registry --group default mcp/oci-registry --port 8092"
echo
echo "3. Run the demo:"
echo "   cd demos/vmcp-composition"
echo "   source .venv/bin/activate"
echo "   python3 demo.py"
echo
