"""Tests for Talos MCP Server."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import yaml

from talos_mcp_server.talos_client import TalosClient, TalosConfig
from talos_mcp_server.server import create_server


class TestTalosConfig:
    """Tests for TalosConfig class."""

    def test_config_initialization_with_path(self):
        """Test config initialization with explicit path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'context': 'test-cluster',
                'contexts': {
                    'test-cluster': {
                        'endpoints': ['192.168.1.10:50000'],
                        'ca': 'Y2EtY2VydA==',  # base64 encoded 'ca-cert'
                        'crt': 'Y2xpZW50LWNlcnQ=',  # base64 encoded 'client-cert'
                        'key': 'Y2xpZW50LWtleQ=='  # base64 encoded 'client-key'
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = TalosConfig(config_path)
            assert config.context_name == 'test-cluster'
            assert config.get_endpoints() == ['192.168.1.10:50000']
            assert config.get_ca_cert() == b'ca-cert'
        finally:
            Path(config_path).unlink()
    
    def test_config_missing_file(self):
        """Test config with non-existent file."""
        config = TalosConfig('/nonexistent/path')
        assert config.config == {}
        assert config.context_name is None


class TestTalosClient:
    """Tests for TalosClient class."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'context': 'test-cluster',
                'contexts': {
                    'test-cluster': {
                        'endpoints': ['192.168.1.10:50000']
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            client = TalosClient(config_path)
            assert client.config.context_name == 'test-cluster'
            assert client.channel is None
        finally:
            Path(config_path).unlink()
    
    @pytest.mark.asyncio
    async def test_get_version(self):
        """Test getting version information."""
        client = TalosClient()
        # Mock the connect method
        with patch.object(client, 'connect', new_callable=AsyncMock):
            version = await client.get_version()
            assert 'version' in version
            assert 'platform' in version
            assert 'arch' in version
    
    @pytest.mark.asyncio
    async def test_list_containers(self):
        """Test listing containers."""
        client = TalosClient()
        with patch.object(client, 'connect', new_callable=AsyncMock):
            containers = await client.list_containers('k8s.io')
            assert isinstance(containers, list)
            if containers:
                assert 'namespace' in containers[0]
                assert 'id' in containers[0]
    
    @pytest.mark.asyncio
    async def test_get_system_stats(self):
        """Test getting system statistics."""
        client = TalosClient()
        with patch.object(client, 'connect', new_callable=AsyncMock):
            stats = await client.get_system_stats()
            assert 'cpu' in stats
            assert 'memory' in stats
            assert 'disk' in stats


class TestMCPServer:
    """Tests for MCP server."""

    def test_server_creation(self):
        """Test MCP server creation."""
        server = create_server()
        assert server is not None
        assert server.name == "talos-mcp-server"
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        server = create_server()
        
        # Get the list_tools handler
        tools = await server._tool_manager.list_tools()
        
        assert len(tools) > 0
        tool_names = [tool.name for tool in tools]
        
        # Check for expected tools
        expected_tools = [
            'talos_version',
            'talos_list_containers',
            'talos_system_stats',
            'talos_service_logs'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names
    
    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Test listing available prompts."""
        server = create_server()
        
        # Get the list_prompts handler
        prompts = await server._prompt_manager.list_prompts()
        
        assert len(prompts) > 0
        prompt_names = [prompt.name for prompt in prompts]
        
        # Check for expected prompts
        assert 'cluster-health-check' in prompt_names
        assert 'upgrade-plan' in prompt_names


@pytest.fixture
def mock_talos_config():
    """Fixture for mock Talos configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            'context': 'test-cluster',
            'contexts': {
                'test-cluster': {
                    'endpoints': ['192.168.1.10:50000', '192.168.1.11:50000'],
                    'ca': 'Y2EtY2VydA==',
                    'crt': 'Y2xpZW50LWNlcnQ=',
                    'key': 'Y2xpZW50LWtleQ=='
                }
            }
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    yield config_path
    
    Path(config_path).unlink()


def test_integration_with_mock_config(mock_talos_config):
    """Integration test with mock configuration."""
    config = TalosConfig(mock_talos_config)
    assert config.context_name == 'test-cluster'
    assert len(config.get_endpoints()) == 2
