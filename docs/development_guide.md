# Development Guide

This guide provides information for developers who want to contribute to or extend the LangGraph + Obsidian integration.

## Project Structure

```
├── api_gateway/          # FastAPI service that wraps Obsidian REST endpoints
│   ├── __init__.py
│   ├── main.py           # Main FastAPI application
│   ├── config.py         # Configuration management
│   └── obsidian_client.py # Obsidian API client wrapper
├── mcp_tools/            # MCP tool implementations
│   ├── __init__.py
│   ├── base.py           # Base MCP tool class
│   ├── registry.py       # Tool registry
│   ├── list_files.py     # List files tool
│   ├── read_note.py      # Read note tool
│   ├── put_file.py       # Put file tool
│   └── patch_file.py     # Patch file tool
├── indexer/              # Indexing and retrieval layer
│   ├── __init__.py
│   ├── vault_indexer.py  # Vault indexing functionality
│   └── hybrid_retriever.py # Hybrid search functionality
├── vector_db/            # Vector database integration
│   ├── __init__.py
│   └── chroma_client.py  # ChromaDB client
├── graph_db/             # Graph database schema and operations
│   ├── __init__.py
│   └── graph_client.py   # SQLite graph database client
├── utils/                # Utility functions and helpers
│   ├── __init__.py
│   ├── safe_write.py     # Safe write operations
│   └── tracing.py        # Tracing and logging
├── tests/                # Unit and integration tests
├── docker/               # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                 # Documentation
│   ├── usage_examples.md
│   └── api_reference.md
├── requirements.txt      # Python dependencies
├── README.md             # Project overview
└── .dockerignore         # Docker ignore file
```

## Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd langgraph-obsidian-integration
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies (optional):
   ```bash
   pip install pytest pytest-asyncio black flake8 mypy
   ```

## Code Style and Formatting

This project follows PEP 8 style guidelines. We recommend using the following tools:

1. **Black** for code formatting:
   ```bash
   black .
   ```

2. **Flake8** for linting:
   ```bash
   flake8 .
   ```

3. **Mypy** for type checking:
   ```bash
   mypy .
   ```

## Testing

### Unit Tests

Unit tests are located in the `tests/` directory. To run unit tests:

```bash
python -m pytest tests/unit/
```

### Integration Tests

Integration tests require a running Obsidian instance with the Local REST API plugin enabled. To run integration tests:

```bash
python -m pytest tests/integration/
```

### Test Structure

```
tests/
├── unit/
│   ├── test_api_gateway.py
│   ├── test_mcp_tools.py
│   ├── test_indexer.py
│   ├── test_vector_db.py
│   ├── test_graph_db.py
│   └── test_utils.py
├── integration/
│   ├── test_obsidian_api.py
│   ├── test_mcp_integration.py
│   └── test_search.py
└── conftest.py
```

## Adding New Features

### Adding a New MCP Tool

1. Create a new file in the `mcp_tools/` directory:
   ```python
   # mcp_tools/new_tool.py
   from mcp_tools.base import MCPTool
   from typing import Dict, Any
   
   class NewTool(MCPTool):
       def __init__(self):
           super().__init__(
               name="new_tool_name",
               description="Description of the new tool"
           )
       
       async def __call__(self, **kwargs) -> Dict[str, Any]:
           # Implementation here
           pass
       
       def _get_parameters_schema(self) -> Dict[str, Any]:
           # Return the JSON schema for parameters
           pass
   ```

2. Register the tool in `mcp_tools/registry.py`:
   ```python
   from mcp_tools.new_tool import NewTool
   
   def _register_default_tools(self):
       # ... existing tools ...
       self.register_tool(NewTool())
   ```

### Extending the Indexer

1. Modify `indexer/vault_indexer.py` to add new chunking strategies or processing logic
2. Update `vector_db/chroma_client.py` to add new vector operations
3. Extend `graph_db/graph_client.py` to add new graph operations

### Adding New API Endpoints

1. Add new endpoints in `api_gateway/main.py`
2. Create corresponding request/response models
3. Implement the business logic
4. Add appropriate tracing and error handling

## Database Schema Changes

### Vector Database

The vector database uses ChromaDB. Schema changes are handled automatically by ChromaDB, but you should:

1. Update the collection schema in `vector_db/chroma_client.py`
2. Update the indexing logic in `indexer/vault_indexer.py`
3. Update the search logic in `indexer/hybrid_retriever.py`

### Graph Database

The graph database uses SQLite. To modify the schema:

1. Update the table definitions in `graph_db/graph_client.py`
2. Add migration logic if needed
3. Update the data access methods

## Docker Development

### Building the Docker Image

```bash
cd docker
docker build -t langgraph-obsidian .
```

### Running in Development Mode

```bash
docker-compose up --build
```

### Debugging Docker Containers

```bash
# View logs
docker-compose logs

# Access container shell
docker-compose exec langgraph-obsidian /bin/bash

# View running processes
docker-compose exec langgraph-obsidian ps aux
```

## Debugging

### Logging

The application uses Python's built-in logging module. To enable debug logging:

```bash
export LOG_LEVEL=DEBUG
```

### Tracing

Function calls and tool executions are traced using the tracing utilities in `utils/tracing.py`. To add tracing to a new function:

```python
from utils.tracing import trace_function_call

def my_function(param1, param2):
    trace_function_call("my_function", param1=param1, param2=param2)
    # Function implementation
```

## Performance Considerations

### Caching

Consider implementing caching for frequently accessed data:

1. Use Redis or Memcached for distributed caching
2. Implement in-memory caching for single-instance deployments
3. Add cache invalidation strategies

### Pagination

For large datasets, implement pagination:

1. Add cursor-based pagination to list endpoints
2. Limit the number of results per page
3. Provide continuation tokens

### Asynchronous Processing

For long-running operations, consider using asynchronous processing:

1. Use Celery or similar task queues
2. Implement background job processing
3. Provide status endpoints for tracking progress

## Security Considerations

### Input Validation

All API inputs should be validated:

1. Use Pydantic models for request validation
2. Sanitize user inputs
3. Implement rate limiting

### Authentication

For production deployments, implement authentication:

1. Add JWT token authentication
2. Implement API key authentication
3. Use OAuth2 for third-party integrations

### Authorization

Implement role-based access control:

1. Define user roles and permissions
2. Implement access control checks
3. Log security-related events

## Deployment Considerations

### Environment Configuration

Use environment variables for configuration:

1. Store secrets in environment variables
2. Use different configurations for development/production
3. Implement configuration validation

### Monitoring

Implement application monitoring:

1. Add health check endpoints
2. Implement application metrics
3. Set up alerting for critical issues

### Backup and Recovery

Implement data backup strategies:

1. Regular backups of vector database
2. Regular backups of graph database
3. Implement disaster recovery procedures

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Review Guidelines

1. Review code for adherence to style guidelines
2. Check for proper error handling
3. Verify test coverage
4. Ensure documentation is updated
5. Check for security considerations

### Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create a git tag
4. Build and push Docker images
5. Update documentation