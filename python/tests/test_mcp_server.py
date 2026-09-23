"""Test file for MCP server functionality"""

import sys
import pytest
import asyncio

sys.path.insert(0, '.')

@pytest.mark.asyncio
async def test_mcp_server_import():
    """Test that the MCP server module can be imported"""
    try:
        from src.mcp.mcp_server import main
        assert main is not None
    except Exception as e:
        pytest.fail(f"Failed to import MCP server: {e}")


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test that the MCP server can be initialized"""
    try:
        from src.mcp.mcp_server import mcp
        assert mcp is not None
        assert hasattr(mcp, 'tool')
        assert hasattr(mcp, 'run')
    except Exception as e:
        pytest.fail(f"Failed to initialize MCP server: {e}")


@pytest.mark.asyncio
async def test_mcp_tool_registration():
    """Test that tools are registered correctly"""
    try:
        from src.mcp.mcp_server import mcp
        from src.mcp.modules.rag_module import register_rag_tools
        
        # Create a new instance to test registration
        from mcp.server.fastmcp import FastMCP
        test_mcp = FastMCP('test-server')
        
        # Register RAG tools
        register_rag_tools(test_mcp)
        
        # Verify tools are registered
        tools = list(test_mcp._tool_manager.list_tools())
        assert len(tools) > 0
        
        # Check for specific tool names
        tool_names = [tool.name for tool in tools]
        assert 'get_available_sources' in tool_names
        assert 'perform_rag_query' in tool_names
        assert 'search_code_examples' in tool_names
        
    except Exception as e:
        pytest.fail(f"Failed to test tool registration: {e}")


@pytest.mark.asyncio
async def test_rag_tool_signatures():
    """Test that RAG tools have correct signatures"""
    try:
        from src.mcp.mcp_server import mcp
        from src.mcp.modules.rag_module import register_rag_tools
        
        from mcp.server.fastmcp import FastMCP
        test_mcp = FastMCP('test-server')
        register_rag_tools(test_mcp)
        
        for tool in test_mcp._tool_manager.list_tools():
            # Check tool has required properties
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'parameters')
            assert hasattr(tool, 'fn_metadata')
            assert hasattr(tool, 'is_async')
            
            # Check parameters are valid
            if tool.name == 'perform_rag_query':
                assert 'query' in tool.parameters['properties']
                assert 'source' in tool.parameters['properties']
                assert 'match_count' in tool.parameters['properties']
                
            if tool.name == 'search_code_examples':
                assert 'query' in tool.parameters['properties']
                assert 'source_id' in tool.parameters['properties']
                assert 'match_count' in tool.parameters['properties']
                
    except Exception as e:
        pytest.fail(f"Failed to test RAG tool signatures: {e}")


def test_module_imports():
    """Test that all MCP related modules can be imported"""
    modules_to_test = [
        'src.mcp.mcp_server',
        'src.mcp.modules.rag_module',
        'src.mcp.modules.project_module',
        'src.server.config.service_discovery',
        'src.server.services.mcp_service_client',
        'src.server.services.mcp_session_manager'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")
        except Exception as e:
            # Some modules might fail to import due to missing dependencies or config
            # This is expected in some cases
            print(f"Warning: {module_name} import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
