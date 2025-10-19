# Architecture Documentation

This document describes the architecture, design decisions, and implementation details of the Talos MCP Server.

## Overview

The Talos MCP Server is a Model Context Protocol (MCP) server that provides AI assistants with programmatic access to Talos Linux clusters. It acts as a bridge between AI systems and Talos infrastructure, enabling intelligent cluster management and automation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AI Assistant                         │
│                   (Claude, etc.)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ MCP Protocol (stdio/SSE)
                        │
┌───────────────────────▼─────────────────────────────────┐
│                 Talos MCP Server                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │              MCP Server Layer                   │   │
│  │  - Tool Registration                            │   │
│  │  - Request Handling                             │   │
│  │  - Prompt Management                            │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           Talos Client Layer                    │   │
│  │  - Configuration Management                     │   │
│  │  - gRPC Channel Management                      │   │
│  │  - API Method Wrappers                          │   │
│  └──────────────────┬──────────────────────────────┘   │
└───────────────────┬─┴──────────────────────────────────┘
                    │
                    │ gRPC/TLS
                    │
┌───────────────────▼─────────────────────────────────────┐
│              Talos Linux Cluster                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │   Node 1   │  │   Node 2   │  │   Node 3   │       │
│  │  (Control) │  │  (Control) │  │  (Worker)  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. MCP Server Layer (`server.py`)

**Responsibilities:**
- Implements the MCP protocol using the official Python SDK
- Registers and manages available tools
- Handles incoming requests from AI assistants
- Validates and routes tool calls
- Manages prompts for common operations
- Error handling and logging

**Key Classes/Functions:**
- `create_server()`: Factory function that creates and configures the MCP server
- `list_tools()`: Returns available tools to the AI assistant
- `call_tool()`: Handles tool execution requests
- `list_prompts()`: Returns available prompts
- `get_prompt()`: Returns specific prompt content

### 2. Talos Client Layer (`talos_client.py`)

**Responsibilities:**
- Manages Talos configuration file parsing
- Establishes and maintains gRPC connections
- Handles TLS certificate management
- Wraps Talos API calls in Python-friendly methods
- Connection pooling and error recovery

**Key Classes:**

#### `TalosConfig`
- Loads and parses talosconfig YAML file
- Extracts endpoints, certificates, and keys
- Provides accessors for configuration values

#### `TalosClient`
- Manages gRPC channel lifecycle
- Provides high-level methods for Talos operations
- Handles authentication and TLS
- Implements retry logic and error handling

### 3. Tool Layer

Each tool corresponds to a specific Talos operation:

```python
Tool Definition → Client Method → gRPC API Call → Talos Response
```

**Tool Categories:**

1. **Information Tools**
   - `talos_version`: Get version information
   - `talos_system_stats`: System resource statistics
   - `talos_list_containers`: Container listing

2. **Management Tools**
   - `talos_reboot`: Node reboot
   - `talos_apply_config`: Configuration management

3. **Kubernetes Tools**
   - `talos_kubeconfig`: Generate kubeconfig
   - `talos_etcd_status`: Etcd health checks

4. **Logging Tools**
   - `talos_service_logs`: Service log retrieval
   - `talos_dmesg`: Kernel logs (future)

## Design Decisions

### 1. Protocol: MCP with A2A

**Why MCP?**
- Standardized protocol for AI-tool integration
- Growing ecosystem and support
- Native support in Claude Desktop
- Extensible architecture

**Why Agent-to-Agent (A2A)?**
- Enables autonomous operation
- Supports long-running operations
- Better for infrastructure management
- Facilitates multi-step workflows

### 2. Language: Python

**Rationale:**
- Strong gRPC support
- Excellent async/await for concurrent operations
- Rich ecosystem for API development
- MCP SDK availability
- Easy integration with AI tools

### 3. Package Manager: uv

**Benefits:**
- Significantly faster than pip
- Better dependency resolution
- Built-in virtual environment management
- Growing adoption in Python community
- Compatible with standard pyproject.toml

### 4. gRPC Communication

**Why gRPC?**
- Talos API is gRPC-based
- Efficient binary protocol
- Strong typing with Protocol Buffers
- Streaming support for logs
- Built-in TLS support

### 5. Configuration Management

**Design:**
- Follows Talos convention (talosconfig file)
- Supports standard locations and env vars
- Secure credential handling
- Context switching support

## Security Considerations

### 1. Credential Management

```
User Config → Environment → Secure Loading → In-Memory Only
```

- Credentials never logged
- TLS required for production
- Base64 encoding in config files
- No credential caching to disk

### 2. API Access Control

- Read-only operations by default
- Write operations clearly marked
- Require explicit confirmation for destructive ops
- Audit logging of all operations

### 3. Network Security

- TLS 1.3 for gRPC connections
- Certificate validation enforced
- Support for client certificates
- Network policies support

## Data Flow

### Tool Execution Flow

```
1. AI Request
   ↓
2. MCP Protocol Parsing
   ↓
3. Tool Validation
   ↓
4. Client Method Call
   ↓
5. gRPC Request
   ↓
6. Talos API
   ↓
7. Response Processing
   ↓
8. Result Formatting
   ↓
9. Return to AI
```

### Configuration Flow

```
1. Load talosconfig YAML
   ↓
2. Select Context
   ↓
3. Extract Credentials
   ↓
4. Decode Base64 Certs
   ↓
5. Create TLS Credentials
   ↓
6. Establish gRPC Channel
```

## Error Handling

### Strategy

1. **Validation Errors**: Caught early at MCP layer
2. **Connection Errors**: Retry with exponential backoff
3. **API Errors**: Gracefully handled and reported
4. **Unexpected Errors**: Logged and returned as user-friendly messages

### Error Hierarchy

```
BaseException
├── ToolExecutionError
│   ├── ConnectionError
│   ├── AuthenticationError
│   └── TimeoutError
└── ConfigurationError
    ├── InvalidConfigError
    └── MissingCredentialsError
```

## Performance Considerations

### 1. Connection Pooling

- Reuse gRPC channels when possible
- Lazy connection establishment
- Automatic reconnection on failure

### 2. Async Operations

- All I/O operations are async
- Non-blocking tool execution
- Concurrent requests supported

### 3. Caching Strategy

- Configuration cached in memory
- No caching of API responses (for consistency)
- Tool metadata cached at startup

## Extensibility

### Adding New Tools

1. Add method to `TalosClient`
2. Register tool in `create_server()`
3. Handle in `call_tool()`
4. Add tests
5. Update documentation

### Supporting New Protocols

The architecture supports adding additional protocols:

```python
class TalosClient:
    async def _call_api(self, method, request):
        # Can switch between gRPC, REST, etc.
        if self.protocol == "grpc":
            return await self._grpc_call(method, request)
        elif self.protocol == "rest":
            return await self._rest_call(method, request)
```

## Testing Strategy

### Unit Tests
- Mock gRPC calls
- Test configuration parsing
- Validate tool registration
- Error handling paths

### Integration Tests
- Real Talos cluster (optional)
- Docker-based test cluster
- End-to-end tool execution

### Performance Tests
- Concurrent request handling
- Connection pool efficiency
- Memory usage under load

## Deployment Options

### 1. Standalone Process
```
User → Claude Desktop → stdio → MCP Server → Talos
```

### 2. Docker Container
```
User → Network → Container → MCP Server → Talos
```

### 3. Kubernetes Deployment
```
User → Ingress → Service → Pod → MCP Server → Talos
```

## Future Enhancements

### Planned Features

1. **Enhanced Monitoring**
   - Metrics collection
   - Prometheus integration
   - Health checks

2. **Advanced Operations**
   - Cluster upgrades
   - Backup/restore
   - Disaster recovery

3. **Multi-Cluster Support**
   - Context switching
   - Cluster comparison
   - Federation support

4. **Caching Layer**
   - Redis integration
   - Response caching
   - Configuration caching

### Potential Improvements

1. **Performance**
   - Connection pooling optimization
   - Parallel operations
   - Streaming responses

2. **Security**
   - Vault integration
   - RBAC support
   - Audit logging

3. **Observability**
   - OpenTelemetry
   - Structured logging
   - Tracing support

## References

- [Talos API Documentation](https://www.talos.dev/latest/reference/api/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://protobuf.dev/)
