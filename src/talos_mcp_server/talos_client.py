"""Talos Linux API client wrapper."""

import asyncio
import base64
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import grpc
import yaml
from google.protobuf import empty_pb2

logger = logging.getLogger(__name__)


class TalosConfig:
    """Talos configuration management."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Talos configuration."""
        if config_path is None:
            config_path = os.environ.get(
                "TALOSCONFIG",
                str(Path.home() / ".talos" / "config")
            )
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.context_name: Optional[str] = None
        self.context: Dict[str, Any] = {}
        
        if self.config_path.exists():
            self.load()
    
    def load(self) -> None:
        """Load Talos configuration from file."""
        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
            
            self.context_name = self.config.get("context")
            if self.context_name:
                contexts = self.config.get("contexts", {})
                self.context = contexts.get(self.context_name, {})
                logger.info(f"Loaded Talos config for context: {self.context_name}")
            else:
                logger.warning("No context specified in Talos config")
        except Exception as e:
            logger.error(f"Failed to load Talos config: {e}")
            raise
    
    def get_endpoints(self) -> List[str]:
        """Get cluster endpoints."""
        return self.context.get("endpoints", [])
    
    def get_ca_cert(self) -> Optional[bytes]:
        """Get CA certificate."""
        ca = self.context.get("ca")
        if ca:
            return base64.b64decode(ca)
        return None
    
    def get_client_cert(self) -> Optional[bytes]:
        """Get client certificate."""
        crt = self.context.get("crt")
        if crt:
            return base64.b64decode(crt)
        return None
    
    def get_client_key(self) -> Optional[bytes]:
        """Get client key."""
        key = self.context.get("key")
        if key:
            return base64.b64decode(key)
        return None


class TalosClient:
    """Talos Linux API client."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Talos client."""
        self.config = TalosConfig(config_path)
        self.channel: Optional[grpc.aio.Channel] = None
    
    async def connect(self, endpoint: Optional[str] = None) -> grpc.aio.Channel:
        """Create gRPC channel to Talos endpoint."""
        if self.channel is not None:
            return self.channel
        
        endpoints = self.config.get_endpoints()
        if not endpoints:
            raise ValueError("No endpoints configured")
        
        target_endpoint = endpoint or endpoints[0]
        
        # Setup TLS credentials
        ca_cert = self.config.get_ca_cert()
        client_cert = self.config.get_client_cert()
        client_key = self.config.get_client_key()
        
        if ca_cert and client_cert and client_key:
            credentials = grpc.ssl_channel_credentials(
                root_certificates=ca_cert,
                private_key=client_key,
                certificate_chain=client_cert
            )
            self.channel = grpc.aio.secure_channel(target_endpoint, credentials)
            logger.info(f"Connected to Talos endpoint: {target_endpoint} (TLS)")
        else:
            # For development/testing - insecure connection
            self.channel = grpc.aio.insecure_channel(target_endpoint)
            logger.warning(f"Connected to Talos endpoint: {target_endpoint} (INSECURE)")
        
        return self.channel
    
    async def close(self) -> None:
        """Close gRPC channel."""
        if self.channel:
            await self.channel.close()
            self.channel = None
    
    async def get_version(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get Talos version information."""
        # This would use the actual gRPC stub - simplified for example
        try:
            channel = await self.connect(endpoint)
            # In a real implementation, you would use the generated proto stubs:
            # from talos.machine import machine_pb2, machine_pb2_grpc
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # response = await stub.Version(empty_pb2.Empty())
            
            # For now, return mock data
            return {
                "version": "v1.9.0",
                "platform": "metal",
                "arch": "amd64"
            }
        except Exception as e:
            logger.error(f"Failed to get version: {e}")
            raise
    
    async def list_containers(
        self,
        namespace: str = "k8s.io",
        endpoint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List containers on a node."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = machine_pb2.ContainersRequest(namespace=namespace)
            # response = await stub.Containers(request)
            
            return [
                {
                    "namespace": namespace,
                    "id": "example-container-1",
                    "image": "registry.k8s.io/pause:3.9",
                    "status": "running"
                }
            ]
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            raise
    
    async def get_system_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation, you would call multiple endpoints:
            # - CPUInfo
            # - Memory
            # - DiskStats
            # - NetworkDeviceStats
            
            return {
                "cpu": {
                    "cores": 8,
                    "usage_percent": 35.2
                },
                "memory": {
                    "total_bytes": 16000000000,
                    "available_bytes": 8000000000,
                    "usage_percent": 50.0
                },
                "disk": {
                    "total_bytes": 500000000000,
                    "available_bytes": 250000000000,
                    "usage_percent": 50.0
                }
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            raise
    
    async def get_service_logs(
        self,
        service: str,
        tail_lines: int = 100,
        endpoint: Optional[str] = None
    ) -> str:
        """Get service logs."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = machine_pb2.LogsRequest(namespace="system", id=service, tail_lines=tail_lines)
            # stream = stub.Logs(request)
            # logs = []
            # async for response in stream:
            #     logs.append(response.bytes.decode())
            
            return f"Sample logs for service: {service}\nLine 1\nLine 2\n..."
        except Exception as e:
            logger.error(f"Failed to get service logs: {e}")
            raise
    
    async def reboot_node(
        self,
        endpoint: Optional[str] = None,
        mode: str = "default"
    ) -> Dict[str, str]:
        """Reboot a node."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = machine_pb2.RebootRequest(mode=mode)
            # response = await stub.Reboot(request)
            
            return {
                "status": "success",
                "message": f"Node {endpoint} reboot initiated"
            }
        except Exception as e:
            logger.error(f"Failed to reboot node: {e}")
            raise
    
    async def get_kubernetes_config(
        self,
        endpoint: Optional[str] = None
    ) -> str:
        """Get Kubernetes config (kubeconfig)."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = machine_pb2.GenerateClientConfigurationRequest()
            # response = await stub.GenerateClientConfiguration(request)
            
            return "apiVersion: v1\nkind: Config\n..."
        except Exception as e:
            logger.error(f"Failed to get kubeconfig: {e}")
            raise
    
    async def apply_configuration(
        self,
        config: str,
        endpoint: Optional[str] = None,
        mode: str = "auto"
    ) -> Dict[str, str]:
        """Apply machine configuration."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = machine_pb2.ApplyConfigurationRequest(
            #     data=config.encode(),
            #     mode=mode
            # )
            # response = await stub.ApplyConfiguration(request)
            
            return {
                "status": "success",
                "message": "Configuration applied successfully"
            }
        except Exception as e:
            logger.error(f"Failed to apply configuration: {e}")
            raise
    
    async def get_etcd_status(
        self,
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get etcd cluster status."""
        try:
            channel = await self.connect(endpoint)
            # In real implementation:
            # stub = machine_pb2_grpc.MachineServiceStub(channel)
            # request = empty_pb2.Empty()
            # response = await stub.EtcdStatus(request)
            
            return {
                "member_id": "12345",
                "leader_id": "12345",
                "raft_term": 1,
                "cluster_size": 3,
                "healthy": True
            }
        except Exception as e:
            logger.error(f"Failed to get etcd status: {e}")
            raise


# For testing purposes
async def main() -> None:
    """Test the Talos client."""
    client = TalosClient()
    
    try:
        version = await client.get_version()
        print(f"Version: {version}")
        
        containers = await client.list_containers()
        print(f"Containers: {containers}")
        
        stats = await client.get_system_stats()
        print(f"Stats: {stats}")
    finally:
        await client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
