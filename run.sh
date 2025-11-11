#!/bin/sh
# STDIO mode startup script - suitable for local tool integration
set -e

# Change to script directory
cd "$(dirname "$0")"

# Create independent virtual environment (if it doesn't exist)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..." >&2
    uv venv
    echo "Installing dependencies..." >&2
    echo "Note: Dependency installation may take several minutes. Please wait..." >&2
    uv sync
fi

# Start STDIO mode MCP server
uv run server.py --transport stdio
