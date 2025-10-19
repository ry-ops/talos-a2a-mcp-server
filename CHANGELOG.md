# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Talos MCP Server
- Core MCP server implementation with A2A protocol support
- Talos API client wrapper with gRPC support
- Machine management tools:
  - `talos_version` - Get version information
  - `talos_reboot` - Reboot nodes
  - `talos_list_containers` - List containers
  - `talos_system_stats` - Get system statistics
  - `talos_service_logs` - View service logs
- Configuration tools:
  - `talos_apply_config` - Apply machine configuration
- Kubernetes tools:
  - `talos_kubeconfig` - Generate kubeconfig
  - `talos_etcd_status` - Check etcd health
- Built-in prompts for common operations:
  - Cluster health check
  - Upgrade planning
- Comprehensive test suite
- GitHub Actions CI/CD pipeline
- Docker support
- Documentation and examples

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- TLS support for secure Talos API communication
- Configuration file handling with proper permissions

## [0.1.0] - 2025-01-XX

### Added
- Initial project setup
- Basic MCP server functionality
- Talos API integration
- Core tools and prompts
- Documentation and examples

[Unreleased]: https://github.com/yourusername/talos-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/talos-mcp-server/releases/tag/v0.1.0
