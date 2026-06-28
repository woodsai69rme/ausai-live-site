# Kilo CLI Complete Setup Guide

## Overview
This document provides a comprehensive guide to setting up and optimizing Kilo CLI with MCP servers, skills, and best coding practices.

## 1. Kilo CLI Installation & Configuration

### Current Status
- **Installation Method**: Bun package manager
- **Version**: Latest (5.10.x)
- **Location**: `.config/kilo/`

### Configuration File
Create or update `.claude.json` in your home directory:

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "python",
      "args": ["-m", "src.mcp.mcp_server"],
      "env": {
        "ARCHON_MCP_PORT": "8051"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  },
  "skills": {
    "enabled": true,
    "priority": [
      "python-*",
      "azure-*",
      "security-*",
      "mcp-*"
    ]
  },
  "codingStandards": {
    "strictTypes": true,
    "errorHandling": "strict",
    "logging": "detailed"
  }
}
```

## 2. MCP Servers Setup

### Archon MCP Server
- **Port**: 8051
- **Transport**: SSE
- **Tools**:
  - `get_available_sources` - List knowledge base sources
  - `perform_rag_query` - Search vector database
  - `search_code_examples` - Find code examples

### Custom MCP Servers
Add to your configuration:

```json
{
  "mcpServers": {
    "custom-rag": {
      "command": "python",
      "args": ["-m", "src.mcp.mcp_server"],
      "cwd": "/path/to/project"
    }
  }
}
```

## 3. Skills System

### Available Categories
- **Cloud**: Azure, AWS, GCP, Kubernetes
- **Security**: Authentication, Compliance, Auditing
- **Development**: Python, JavaScript, TypeScript, React
- **Testing**: Unit, Integration, E2E
- **Database**: PostgreSQL, SQL, NoSQL
- **DevOps**: Docker, CI/CD, Infrastructure

### Custom Skills
Create skills in `.agents/skills/` directory:

```
.agents/skills/
├── custom-skill/
│   ├── SKILL.md
│   └── implementation.py
```

## 4. Coding Standards

### Python Best Practices
- Use type hints
- Implement proper error handling
- Add detailed logging
- Follow PEP 8

### JavaScript/TypeScript
- Use strict mode
- Implement proper error boundaries
- Add TypeScript types

## 5. Environment Configuration

### Required Environment Variables
```bash
# MCP Server
ARCHON_MCP_PORT=8051
ARCHON_SERVER_PORT=8181

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# AI Models
OPENROUTER_API_KEY=xxx
```

## 6. Quick Start Commands

```bash
# Start MCP Server
cd /c/Users/karma/python
python -m src.mcp.mcp_server

# Test MCP Tools
python -m pytest tests/test_mcp_server.py -v

# Run Kilo
kilo --help

# List available skills
kilo skills list
```

## 7. Performance Optimization

### MCP Server
1. Use HTTP-based communication
2. Implement caching
3. Add connection pooling
4. Configure timeouts

### Skills
1. Enable lazy loading
2. Add caching
3. Optimize imports

## 8. Troubleshooting

### Common Issues
1. **Port already in use**: Kill existing process or change port
2. **Import errors**: Check Python path and dependencies
3. **Permission errors**: Run as administrator or fix permissions

### Debug Commands
```bash
# Check running processes
netstat -ano | findstr 8051

# Test MCP connection
curl http://localhost:8051/health

# View logs
tail -f /tmp/mcp_server.log
```

## 9. Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Validate inputs** - Use Pydantic models
3. **Handle errors properly** - Detailed error messages
4. **Log securely** - Mask sensitive data

## 10. Resources

- [Kilo Documentation](https://kilo.ai/docs)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Skills Library](https://github.com/kilo-ai/skills)
