# Quick Start Guide

Get up and running with Talos MCP Server in minutes!

## Prerequisites

- Python 3.11 or higher
- A Talos Linux cluster with access credentials
- [uv](https://github.com/astral-sh/uv) package manager (will be installed by setup script)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/talos-mcp-server.git
cd talos-mcp-server

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/talos-mcp-server.git
cd talos-mcp-server

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Copy environment file
cp .env.example .env
```

## Configuration

### 1. Get Your Talos Configuration

If you already have a Talos cluster:

```bash
# If you have talosctl installed
talosctl config merge ~/.talos/config

# Or specify a custom path
export TALOSCONFIG=/path/to/your/talosconfig
```

If you need to create a new cluster:

```bash
# Generate configuration
talosctl gen config my-cluster https://cluster-endpoint:6443

# The talosconfig will be created in the current directory
```

### 2. Configure the MCP Server

Edit `.env` file:

```bash
TALOSCONFIG=/path/to/your/talosconfig
LOG_LEVEL=INFO
```

## Running the Server

### Standalone Mode

```bash
# Using uv
uv run talos-mcp-server

# Or using make
make run

# With custom config
uv run talos-mcp-server --talosconfig /path/to/config
```

### With Claude Desktop

1. Open Claude Desktop configuration:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "talos": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/talos-mcp-server",
        "run",
        "talos-mcp-server"
      ],
      "env": {
        "TALOSCONFIG": "/path/to/your/talosconfig"
      }
    }
  }
}
```

3. Restart Claude Desktop

### Using Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f talos-mcp-server

# Stop
docker-compose down
```

## Testing the Server

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
make test-cov

# Specific test file
uv run pytest tests/test_server.py -v
```

### Manual Testing

Once the server is running with Claude Desktop, try these example queries:

1. **Check Cluster Version**
   ```
   What version of Talos is running on my cluster?
   ```

2. **List Containers**
   ```
   Show me all containers running in the k8s.io namespace
   ```

3. **Get System Stats**
   ```
   What are the current system resources (CPU, memory, disk) on my nodes?
   ```

4. **Check Cluster Health**
   ```
   Please run a comprehensive health check on my Talos cluster
   ```

## Common Issues

### Issue: "No endpoints configured"

**Solution:** Make sure your talosconfig file exists and is properly formatted. Check the path in your `.env` file.

```bash
# Verify config file exists
ls -la $TALOSCONFIG

# Check config format
cat $TALOSCONFIG
```

### Issue: "Connection refused"

**Solution:** 
1. Verify your cluster endpoints are accessible
2. Check firewall rules
3. Ensure port 50000 (default Talos API port) is open

```bash
# Test connectivity
telnet 192.168.1.10 50000

# Or using talosctl
talosctl version --nodes 192.168.1.10
```

### Issue: "TLS certificate error"

**Solution:** Ensure your CA certificate, client certificate, and key are properly encoded in the talosconfig.

```bash
# Verify base64 encoding
echo "LS0tLS..." | base64 -d | openssl x509 -text -noout
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [examples/](examples/) for configuration samples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Join the Talos Slack community for support

## Development

```bash
# Install dev dependencies
make dev

# Run linter
make lint

# Format code
make format

# Type checking
make type-check

# Run all checks
make check
```

## Useful Commands

```bash
# Clean build artifacts
make clean

# Build package
make build

# View all available commands
make help
```

## Getting Help

- GitHub Issues: https://github.com/yourusername/talos-mcp-server/issues
- Talos Documentation: https://www.talos.dev/
- MCP Documentation: https://modelcontextprotocol.io/
- Talos Slack: https://slack.dev.talos-systems.io/

## Resources

- [Talos Linux Documentation](https://www.talos.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [uv Documentation](https://github.com/astral-sh/uv)
