#!/bin/bash
# Setup script for Talos MCP Server

set -e

echo "🚀 Setting up Talos MCP Server..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11 or higher is required but not found."
    echo "Please install Python 3.11+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the uv environment
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ Failed to install uv. Please install it manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

echo "✅ uv package manager found"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras

echo "✅ Dependencies installed"

# Check for Talos configuration
TALOSCONFIG="${TALOSCONFIG:-$HOME/.talos/config}"

if [ ! -f "$TALOSCONFIG" ]; then
    echo "⚠️  Warning: Talos configuration file not found at $TALOSCONFIG"
    echo "   Please ensure you have a valid talosconfig file."
    echo "   You can set the TALOSCONFIG environment variable to specify a custom path."
    echo ""
    echo "   Example talosconfig is available in: examples/config.yaml"
else
    echo "✅ Talos configuration found at $TALOSCONFIG"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Talos MCP Server Configuration
TALOSCONFIG=$TALOSCONFIG
LOG_LEVEL=INFO
EOF
    echo "✅ .env file created"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Configure your talosconfig file (if not already done)"
echo "  2. Run the server: uv run talos-mcp-server"
echo "  3. Or run tests: uv run pytest"
echo ""
echo "For Claude Desktop integration, add this to your config:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "talos": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/talos-mcp-server",
        "run",
        "talos-mcp-server"
      ],
      "env": {
        "TALOSCONFIG": "/path/to/your/talosconfig"
      }
    }
  }
}
EOF
echo ""
echo "For more information, see README.md"
