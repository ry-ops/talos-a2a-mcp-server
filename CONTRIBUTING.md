# Contributing to Talos MCP Server

Thank you for your interest in contributing to the Talos MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Detailed steps to reproduce the problem
- Expected behavior vs. actual behavior
- Your environment (OS, Python version, Talos version)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed feature
- Explain why this enhancement would be useful
- Provide examples of how it would work

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the code style guidelines
4. Add or update tests as necessary
5. Ensure all tests pass
6. Update documentation if needed
7. Commit your changes with clear commit messages
8. Push to your fork and submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- Access to a Talos Linux cluster (for integration testing)

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/talos-mcp-server.git
   cd talos-mcp-server
   ```

2. Install dependencies:
   ```bash
   uv sync --all-extras
   ```

3. Set up pre-commit hooks (optional but recommended):
   ```bash
   uv run pre-commit install
   ```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run with verbose output
uv run pytest -v
```

### Code Style

We use several tools to maintain code quality:

#### Linting

```bash
# Check code style
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

#### Type Checking

```bash
# Run type checker
uv run mypy src
```

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and concise
- Prefer explicit over implicit
- Use meaningful variable and function names

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update examples/ if adding new features
- Include inline comments for complex logic

## Project Structure

```
talos-mcp-server/
├── src/
│   └── talos_mcp_server/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server implementation
│       ├── talos_client.py      # Talos API client
│       └── tools/               # Tool implementations
├── tests/                       # Test files
├── examples/                    # Example configurations
├── .github/                     # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml
├── pyproject.toml              # Project configuration
├── README.md                   # User documentation
└── CONTRIBUTING.md            # This file
```

## Adding New Tools

To add a new tool to the MCP server:

1. Implement the tool logic in `talos_client.py`:
   ```python
   async def my_new_tool(self, param: str) -> Dict[str, Any]:
       """Tool description."""
       # Implementation
       pass
   ```

2. Register the tool in `server.py` in the `list_tools()` function:
   ```python
   Tool(
       name="talos_my_tool",
       description="Tool description",
       inputSchema={
           "type": "object",
           "properties": {
               "param": {
                   "type": "string",
                   "description": "Parameter description"
               }
           },
           "required": ["param"]
       }
   )
   ```

3. Handle the tool call in the `call_tool()` function:
   ```python
   elif name == "talos_my_tool":
       param = arguments["param"]
       result = await talos_client.my_new_tool(param)
       return [TextContent(type="text", text=str(result))]
   ```

4. Add tests for your new tool in `tests/test_server.py`

5. Update README.md to document the new tool

## Testing Guidelines

- Write tests for all new features
- Aim for high code coverage (>80%)
- Use pytest fixtures for common setup
- Mock external dependencies (gRPC calls, etc.)
- Test both success and error cases
- Use descriptive test names

## Commit Message Guidelines

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(tools): add support for etcd snapshot operations

Add new tools for creating and restoring etcd snapshots.
Includes validation and error handling.

Closes #123
```

```
fix(client): handle connection timeout gracefully

Previously, connection timeouts would crash the server.
Now they are caught and logged appropriately.
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will automatically build and publish

## Getting Help

- Check existing issues and discussions
- Join the Talos Slack community
- Read the Talos documentation: https://www.talos.dev/
- Read the MCP documentation: https://modelcontextprotocol.io/

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
