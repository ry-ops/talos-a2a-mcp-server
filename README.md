# Talos Linux MCP Server

An MCP (Model Context Protocol) server that provides AI assistants with the ability to interact with Talos Linux clusters through the Talos API.

## Features

- 🚀 **Full Talos API Integration** - Access to machine management, configuration, and monitoring
- 🤖 **Agent-to-Agent Protocol** - Built with MCP's A2A protocol for reliable communication
- 📦 **Modern Python** - Uses `uv` for fast, reliable dependency management
- 🔐 **Secure by Default** - Supports Talos authentication and TLS
- 📊 **Rich Monitoring** - Query system stats, logs, and cluster health

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Access to a Talos Linux cluster
- Talos configuration file (`talosconfig`)

### Using uv

```bash
# Clone the repository
git clone https://github.com/yourusername/talos-mcp-server.git
cd talos-mcp-server

# Install dependencies
uv sync

# Run the server
uv run talos-mcp-server
```

### Using pip

```bash
pip install talos-mcp-server
```

## Configuration

The server requires a Talos configuration file. You can specify it using:

1. Environment variable: `TALOSCONFIG=/path/to/talosconfig`
2. Default location: `~/.talos/config`
3. Command line argument: `--talosconfig /path/to/talosconfig`

### Example Configuration

```yaml
# config.yaml
context: my-cluster
contexts:
  my-cluster:
    endpoints:
      - 192.168.1.10
      - 192.168.1.11
    ca: <base64-encoded-ca>
    crt: <base64-encoded-cert>
    key: <base64-encoded-key>
```

## Available Tools

The MCP server exposes the following tools to AI assistants:

### Machine Management

- `talos_version` - Get Talos version information
- `talos_reboot` - Reboot a node
- `talos_shutdown` - Shutdown a node
- `talos_upgrade` - Upgrade Talos on a node

### Configuration

- `talos_get_config` - Retrieve current machine configuration
- `talos_apply_config` - Apply new configuration
- `talos_gen_config` - Generate new configuration

### Monitoring & Logs

- `talos_dmesg` - Read kernel logs
- `talos_logs` - Get service logs
- `talos_stats` - Get system statistics (CPU, memory, disk)
- `talos_processes` - List running processes

### Container Management

- `talos_containers` - List containers
- `talos_container_logs` - Get container logs

### Kubernetes

- `talos_kubeconfig` - Generate kubeconfig
- `talos_etcd_status` - Check etcd cluster health

### Network

- `talos_interfaces` - List network interfaces
- `talos_routes` - Show routing table

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
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
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/talos-mcp-server.git
cd talos-mcp-server

# Install development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run mypy src
```

### Project Structure

```
talos-mcp-server/
├── src/
│   └── talos_mcp_server/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── talos_client.py    # Talos API client wrapper
│       └── tools/              # Tool implementations
│           ├── __init__.py
│           ├── machine.py      # Machine management tools
│           ├── config.py       # Configuration tools
│           ├── monitoring.py   # Monitoring and stats tools
│           └── kubernetes.py   # Kubernetes-related tools
├── tests/
│   ├── __init__.py
│   └── test_server.py
├── examples/
│   └── config.yaml
├── pyproject.toml
├── README.md
└── LICENSE
```

## Examples

### Check Cluster Health

```python
# The AI assistant can use these tools:
# 1. Get version information from all nodes
# 2. Check etcd cluster health
# 3. Review system stats
```

### Upgrade Cluster

```python
# The AI assistant can:
# 1. Check current versions
# 2. Plan upgrade strategy
# 3. Execute rolling upgrade
# 4. Verify health after each node
```

## Security Considerations

- Always use TLS for production clusters
- Limit network access to the MCP server
- Use read-only configurations when possible
- Audit AI assistant actions through logs
- Consider using separate credentials for AI access

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details

## Links

- [Talos Linux Documentation](https://www.talos.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Support

- GitHub Issues: https://github.com/yourusername/talos-mcp-server/issues
- Talos Slack: https://slack.dev.talos-systems.io/

## Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Powered by [Talos Linux](https://www.talos.dev/)
- Package management by [uv](https://github.com/astral-sh/uv)
