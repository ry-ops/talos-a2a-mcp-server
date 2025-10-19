"""Main MCP server implementation for Talos Linux."""

import argparse
import asyncio
import logging
import os
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    GetPromptResult,
    Prompt,
    PromptMessage,
)

from .talos_client import TalosClient

logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("talos-mcp-server")
    talos_client: Optional[TalosClient] = None
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available Talos tools."""
        return [
            Tool(
                name="talos_version",
                description="Get Talos Linux version information from a node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port). If not specified, uses first configured endpoint"
                        }
                    }
                }
            ),
            Tool(
                name="talos_list_containers",
                description="List containers running on a Talos node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Container namespace (e.g., 'k8s.io', 'system')",
                            "default": "k8s.io"
                        },
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port)"
                        }
                    }
                }
            ),
            Tool(
                name="talos_system_stats",
                description="Get system statistics (CPU, memory, disk) from a Talos node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port)"
                        }
                    }
                }
            ),
            Tool(
                name="talos_service_logs",
                description="Get logs from a system service on a Talos node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service name (e.g., 'kubelet', 'etcd', 'apid')"
                        },
                        "tail_lines": {
                            "type": "integer",
                            "description": "Number of lines to tail",
                            "default": 100
                        },
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port)"
                        }
                    },
                    "required": ["service"]
                }
            ),
            Tool(
                name="talos_reboot",
                description="Reboot a Talos node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port) to reboot"
                        },
                        "mode": {
                            "type": "string",
                            "description": "Reboot mode: 'default' or 'graceful'",
                            "default": "default"
                        }
                    },
                    "required": ["endpoint"]
                }
            ),
            Tool(
                name="talos_kubeconfig",
                description="Generate kubeconfig for accessing the Kubernetes cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Control plane node endpoint"
                        }
                    }
                }
            ),
            Tool(
                name="talos_etcd_status",
                description="Get etcd cluster health and status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "Control plane node endpoint"
                        }
                    }
                }
            ),
            Tool(
                name="talos_apply_config",
                description="Apply a new machine configuration to a Talos node",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "string",
                            "description": "Machine configuration in YAML format"
                        },
                        "endpoint": {
                            "type": "string",
                            "description": "Node endpoint (IP:port)"
                        },
                        "mode": {
                            "type": "string",
                            "description": "Apply mode: 'auto', 'no-reboot', 'reboot', 'staged'",
                            "default": "auto"
                        }
                    },
                    "required": ["config", "endpoint"]
                }
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        nonlocal talos_client
        
        # Initialize client if needed
        if talos_client is None:
            config_path = os.environ.get("TALOSCONFIG")
            talos_client = TalosClient(config_path)
        
        try:
            if name == "talos_version":
                endpoint = arguments.get("endpoint")
                result = await talos_client.get_version(endpoint)
                return [TextContent(
                    type="text",
                    text=f"Talos Version Information:\n"
                         f"Version: {result.get('version')}\n"
                         f"Platform: {result.get('platform')}\n"
                         f"Architecture: {result.get('arch')}"
                )]
            
            elif name == "talos_list_containers":
                namespace = arguments.get("namespace", "k8s.io")
                endpoint = arguments.get("endpoint")
                containers = await talos_client.list_containers(namespace, endpoint)
                
                container_list = "\n".join([
                    f"- {c['id']}: {c['image']} ({c['status']})"
                    for c in containers
                ])
                
                return [TextContent(
                    type="text",
                    text=f"Containers in namespace '{namespace}':\n{container_list}"
                )]
            
            elif name == "talos_system_stats":
                endpoint = arguments.get("endpoint")
                stats = await talos_client.get_system_stats(endpoint)
                
                return [TextContent(
                    type="text",
                    text=f"System Statistics:\n\n"
                         f"CPU:\n"
                         f"  Cores: {stats['cpu']['cores']}\n"
                         f"  Usage: {stats['cpu']['usage_percent']}%\n\n"
                         f"Memory:\n"
                         f"  Total: {stats['memory']['total_bytes'] / 1e9:.2f} GB\n"
                         f"  Available: {stats['memory']['available_bytes'] / 1e9:.2f} GB\n"
                         f"  Usage: {stats['memory']['usage_percent']}%\n\n"
                         f"Disk:\n"
                         f"  Total: {stats['disk']['total_bytes'] / 1e9:.2f} GB\n"
                         f"  Available: {stats['disk']['available_bytes'] / 1e9:.2f} GB\n"
                         f"  Usage: {stats['disk']['usage_percent']}%"
                )]
            
            elif name == "talos_service_logs":
                service = arguments["service"]
                tail_lines = arguments.get("tail_lines", 100)
                endpoint = arguments.get("endpoint")
                
                logs = await talos_client.get_service_logs(service, tail_lines, endpoint)
                
                return [TextContent(
                    type="text",
                    text=f"Logs for service '{service}' (last {tail_lines} lines):\n\n{logs}"
                )]
            
            elif name == "talos_reboot":
                endpoint = arguments["endpoint"]
                mode = arguments.get("mode", "default")
                
                result = await talos_client.reboot_node(endpoint, mode)
                
                return [TextContent(
                    type="text",
                    text=f"Reboot initiated for {endpoint}\n"
                         f"Status: {result['status']}\n"
                         f"Message: {result['message']}"
                )]
            
            elif name == "talos_kubeconfig":
                endpoint = arguments.get("endpoint")
                
                kubeconfig = await talos_client.get_kubernetes_config(endpoint)
                
                return [TextContent(
                    type="text",
                    text=f"Kubeconfig:\n\n{kubeconfig}"
                )]
            
            elif name == "talos_etcd_status":
                endpoint = arguments.get("endpoint")
                
                status = await talos_client.get_etcd_status(endpoint)
                
                return [TextContent(
                    type="text",
                    text=f"Etcd Cluster Status:\n"
                         f"Member ID: {status['member_id']}\n"
                         f"Leader ID: {status['leader_id']}\n"
                         f"Raft Term: {status['raft_term']}\n"
                         f"Cluster Size: {status['cluster_size']}\n"
                         f"Healthy: {status['healthy']}"
                )]
            
            elif name == "talos_apply_config":
                config = arguments["config"]
                endpoint = arguments["endpoint"]
                mode = arguments.get("mode", "auto")
                
                result = await talos_client.apply_configuration(config, endpoint, mode)
                
                return [TextContent(
                    type="text",
                    text=f"Configuration applied to {endpoint}\n"
                         f"Status: {result['status']}\n"
                         f"Message: {result['message']}"
                )]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
        
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]
    
    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts for Talos operations."""
        return [
            Prompt(
                name="cluster-health-check",
                description="Comprehensive health check for a Talos cluster",
                arguments=[
                    {
                        "name": "endpoints",
                        "description": "Comma-separated list of node endpoints",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="upgrade-plan",
                description="Generate a plan for upgrading a Talos cluster",
                arguments=[
                    {
                        "name": "target_version",
                        "description": "Target Talos version",
                        "required": True
                    }
                ]
            ),
        ]
    
    @server.get_prompt()
    async def get_prompt(name: str, arguments: Dict[str, str] | None) -> GetPromptResult:
        """Get a specific prompt."""
        if name == "cluster-health-check":
            endpoints = arguments.get("endpoints", "all configured") if arguments else "all"
            
            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Please perform a comprehensive health check of the Talos cluster.\n\n"
                                 f"Check the following for nodes: {endpoints}\n"
                                 f"1. Get version information\n"
                                 f"2. Check etcd cluster health\n"
                                 f"3. Review system stats (CPU, memory, disk)\n"
                                 f"4. Check critical service status\n"
                                 f"5. Summarize any issues found"
                        )
                    )
                ]
            )
        
        elif name == "upgrade-plan":
            target = arguments.get("target_version", "latest") if arguments else "latest"
            
            return GetPromptResult(
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Create a detailed upgrade plan for upgrading this Talos cluster to version {target}.\n\n"
                                 f"The plan should include:\n"
                                 f"1. Current cluster version and health status\n"
                                 f"2. Pre-upgrade checks and backups\n"
                                 f"3. Upgrade order (control plane first, then workers)\n"
                                 f"4. Validation steps after each node\n"
                                 f"5. Rollback procedure if issues occur\n"
                                 f"6. Post-upgrade verification"
                        )
                    )
                ]
            )
        
        raise ValueError(f"Unknown prompt: {name}")
    
    return server


async def run_server() -> None:
    """Run the MCP server."""
    server = create_server()
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Talos MCP Server starting...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Talos MCP Server")
    parser.add_argument(
        "--talosconfig",
        type=str,
        help="Path to Talos configuration file"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Set TALOSCONFIG environment variable if provided
    if args.talosconfig:
        os.environ["TALOSCONFIG"] = args.talosconfig
    
    # Run the server
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
