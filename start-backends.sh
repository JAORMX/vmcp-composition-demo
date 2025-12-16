#!/bin/bash
#
# Helper script to start all required backend MCP servers for the demo
# Uses ToolHive CLI to run servers in the 'default' group
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THV_BIN=$(command -v thv || echo "${SCRIPT_DIR}/../../bin/thv")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Backend servers (name -> proxy-port for streamable-http transport)
declare -A BACKENDS=(
    ["fetch"]="8090"
    ["github"]="8091"
    ["oci-registry"]="8092"
)

print_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo
}

start_backends() {
    print_header "Starting Backend MCP Servers"

    # Check if thv binary exists
    if [ ! -f "$THV_BIN" ]; then
        echo -e "${RED}Error: thv binary not found at $THV_BIN${NC}"
        echo -e "${YELLOW}Please run: task build${NC}"
        exit 1
    fi

    for backend in "${!BACKENDS[@]}"; do
        port="${BACKENDS[$backend]}"

        # Check if already running using thv list
        if "$THV_BIN" list --group default 2>/dev/null | grep -q "^$backend"; then
            echo -e "${YELLOW}✓ $backend already running in group 'default'${NC}"
            continue
        fi

        echo -e "${CYAN}→ Starting $backend MCP server on port $port...${NC}"

        # Use ToolHive CLI to run the server from registry
        # - Uses registry server (fetch, github, oci-registry available)
        # - Assigns to 'default' group for vmcp discovery
        # - Sets proxy port for streamable-http transport
        "$THV_BIN" run --name "$backend" --group default --proxy-port "$port" "$backend" &

        # Wait briefly for startup
        sleep 2

        # Verify it started
        if "$THV_BIN" list --group default 2>/dev/null | grep -q "^$backend"; then
            echo -e "${GREEN}✓ $backend started on port $port${NC}"
        else
            echo -e "${RED}✗ $backend failed to start${NC}"
            echo -e "${YELLOW}  Check logs with: thv logs $backend${NC}"
        fi
    done

    echo
    echo -e "${GREEN}Backend servers started in 'default' group!${NC}"
    echo
    echo -e "${CYAN}Check status with:${NC} thv list --group default"
    echo -e "${CYAN}View logs with:${NC} thv logs <backend>"
    echo -e "${CYAN}Stop with:${NC} thv stop <backend>"
    echo -e "${CYAN}Or use:${NC} $0 stop"
    echo
}

stop_backends() {
    print_header "Stopping Backend MCP Servers"

    for backend in "${!BACKENDS[@]}"; do
        # Check if running using thv list
        if ! "$THV_BIN" list --group default 2>/dev/null | grep -q "^$backend"; then
            continue
        fi

        echo -e "${CYAN}→ Stopping $backend...${NC}"
        "$THV_BIN" stop "$backend" 2>/dev/null || true
        echo -e "${GREEN}✓ $backend stopped${NC}"
    done

    echo
    echo -e "${GREEN}All backends stopped${NC}"
    echo
}

show_status() {
    print_header "Backend MCP Server Status"

    echo -e "${CYAN}Servers in 'default' group:${NC}"
    echo

    # Use thv list to show actual status
    "$THV_BIN" list --group default 2>/dev/null || {
        echo -e "${YELLOW}No servers running in 'default' group${NC}"
    }

    echo
}

show_logs() {
    local backend="$1"

    if [ -z "$backend" ]; then
        echo -e "${RED}Error: Please specify a backend${NC}"
        echo -e "${YELLOW}Available: ${!BACKENDS[@]}${NC}"
        exit 1
    fi

    if [[ ! -v BACKENDS[$backend] ]]; then
        echo -e "${RED}Error: Unknown backend: $backend${NC}"
        echo -e "${YELLOW}Available: ${!BACKENDS[@]}${NC}"
        exit 1
    fi

    echo -e "${CYAN}Logs for $backend:${NC}"
    echo -e "${CYAN}─────────────────────────${NC}"
    echo

    # Use thv logs to tail logs
    exec "$THV_BIN" logs "$backend"
}

show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs <backend>}"
    echo
    echo "Commands:"
    echo "  start    - Start all backend MCP servers in 'default' group"
    echo "  stop     - Stop all backend MCP servers"
    echo "  restart  - Restart all backend MCP servers"
    echo "  status   - Show status of all backends"
    echo "  logs     - Tail logs for a specific backend"
    echo
    echo "Backends: ${!BACKENDS[@]}"
    echo
    echo "Note: Uses ToolHive CLI (thv) to manage servers"
    echo
}

# Main
case "${1:-}" in
    start)
        start_backends
        ;;
    stop)
        stop_backends
        ;;
    restart)
        stop_backends
        sleep 1
        start_backends
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
