# MCP Server Testing Guide

This comprehensive testing guide covers all aspects of testing the MCP server, from unit tests to production readiness validation.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Test Suites](#test-suites)
4. [Test Categories](#test-categories)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Production Readiness](#production-readiness)
8. [Troubleshooting](#troubleshooting)

## Test Structure

The test suite is organized into the following structure:

```
tests/
├── tools_test.go                    # Unit tests for MCP tools
├── integration_test.go              # Integration tests with external services
├── end_to_end_test.go              # End-to-end workflow tests
├── performance_test.go              # Performance and load testing
├── api_validation_test.go          # Obsidian API validation tests
├── ollama_validation_test.go       # Ollama integration validation tests
├── mcp_protocol_validation_test.go # MCP protocol compliance tests
├── security_validation_test.go     # Security and vulnerability tests
└── production_readiness_test.go    # Production readiness validation
```

## Running Tests

### Prerequisites

1. **Go Environment**: Ensure Go 1.22+ is installed
2. **Dependencies**: Run `go mod tidy` to install dependencies
3. **Server**: The MCP server should be running (or use mock mode)

### Quick Start

```bash
# Run all tests
go run scripts/run_all_tests.go

# Run specific test suite
go test -v tests/tools_test.go

# Run tests with coverage
go test -v -cover ./tests/...

# Run tests in parallel
go test -v -parallel 4 ./tests/...
```

### Individual Test Execution

```bash
# Unit tests
go test -v tests/tools_test.go

# Integration tests
go test -v tests/integration_test.go

# End-to-end tests
go test -v tests/end_to_end_test.go

# Performance tests
go test -v tests/performance_test.go

# Security tests
go test -v tests/security_validation_test.go

# Production readiness tests
go test -v tests/production_readiness_test.go
```

## Test Suites

### 1. Unit Tests (`tools_test.go`)

**Purpose**: Test individual MCP tools in isolation

**Coverage**:
- Tool parameter validation
- Tool execution logic
- Error handling
- Response formatting
- Mock client integration

**Key Tests**:
- `TestListFilesInVault`
- `TestReadNote`
- `TestSearchVault`
- `TestSemanticSearch`
- `TestCreateNote`
- `TestBulkTag`
- `TestAnalyzeLinks`

### 2. Integration Tests (`integration_test.go`)

**Purpose**: Test integration with external services

**Coverage**:
- Obsidian Local REST API integration
- Ollama LLM integration
- HTTP client functionality
- Error handling and retries
- Authentication

**Key Tests**:
- `TestObsidianAPIConnection`
- `TestOllamaConnection`
- `TestHTTPClientRetryLogic`
- `TestAuthenticationFlow`

### 3. End-to-End Tests (`end_to_end_test.go`)

**Purpose**: Test complete workflows from start to finish

**Coverage**:
- Complete MCP workflows
- Tool chaining
- Data flow validation
- Error propagation
- Performance under realistic conditions

**Key Tests**:
- `TestCompleteSearchWorkflow`
- `TestNoteCreationWorkflow`
- `TestSemanticSearchWorkflow`
- `TestBulkOperationsWorkflow`

### 4. Performance Tests (`performance_test.go`)

**Purpose**: Measure and validate performance characteristics

**Coverage**:
- Response time benchmarks
- Throughput measurements
- Memory usage analysis
- Concurrent request handling
- Load testing

**Key Tests**:
- `TestResponseTimeBenchmarks`
- `TestThroughputMeasurements`
- `TestMemoryUsageAnalysis`
- `TestConcurrentRequestHandling`
- `TestLoadTesting`

### 5. API Validation Tests (`api_validation_test.go`)

**Purpose**: Validate all Obsidian API endpoints and error handling

**Coverage**:
- All Obsidian Local REST API endpoints
- Error response validation
- Status code verification
- Response format validation
- Edge case handling

**Key Tests**:
- `TestAllObsidianEndpoints`
- `TestErrorResponseValidation`
- `TestStatusCodeVerification`
- `TestResponseFormatValidation`

### 6. Ollama Validation Tests (`ollama_validation_test.go`)

**Purpose**: Test Ollama integration with all available models

**Coverage**:
- Model availability testing
- Text generation validation
- Embedding generation testing
- Error handling
- Performance validation

**Key Tests**:
- `TestModelAvailability`
- `TestTextGeneration`
- `TestEmbeddingGeneration`
- `TestErrorHandling`

### 7. MCP Protocol Validation Tests (`mcp_protocol_validation_test.go`)

**Purpose**: Validate MCP protocol compliance and message handling

**Coverage**:
- MCP tool schema validation
- Tool execution compliance
- Message format validation
- Error handling compliance
- Protocol compliance

**Key Tests**:
- `TestMCPToolSchemaValidation`
- `TestMCPToolExecutionValidation`
- `TestMCPMessageFormatValidation`
- `TestMCPErrorHandlingValidation`

### 8. Security Validation Tests (`security_validation_test.go`)

**Purpose**: Test security features and vulnerability prevention

**Coverage**:
- Input validation and sanitization
- Rate limiting
- Authentication mechanisms
- Data sanitization
- Error information disclosure
- Security headers

**Key Tests**:
- `TestInputValidation`
- `TestRateLimiting`
- `TestAuthenticationValidation`
- `TestDataSanitization`
- `TestErrorInformationDisclosure`

### 9. Production Readiness Tests (`production_readiness_test.go`)

**Purpose**: Ensure production readiness with monitoring and health checks

**Coverage**:
- Health check endpoints
- Monitoring and metrics
- Error handling
- Performance under load
- Resource usage
- Graceful shutdown
- Configuration validation

**Key Tests**:
- `TestHealthCheckEndpoints`
- `TestMonitoringAndMetrics`
- `TestErrorHandling`
- `TestPerformanceUnderLoad`
- `TestResourceUsage`

## Test Categories

### Unit Tests
- **Scope**: Individual functions and methods
- **Dependencies**: Mock objects only
- **Speed**: Fast (< 1 second per test)
- **Coverage**: High (90%+)

### Integration Tests
- **Scope**: Component interactions
- **Dependencies**: External services (mocked or real)
- **Speed**: Medium (1-10 seconds per test)
- **Coverage**: Medium (70%+)

### End-to-End Tests
- **Scope**: Complete workflows
- **Dependencies**: Full system
- **Speed**: Slow (10+ seconds per test)
- **Coverage**: Low (50%+)

### Performance Tests
- **Scope**: Performance characteristics
- **Dependencies**: Full system under load
- **Speed**: Very slow (minutes)
- **Coverage**: Performance metrics

### Security Tests
- **Scope**: Security vulnerabilities
- **Dependencies**: Full system
- **Speed**: Medium (1-30 seconds per test)
- **Coverage**: Security aspects

## Performance Testing

### Benchmarks

The performance tests include comprehensive benchmarks:

```go
// Example benchmark
func BenchmarkSearchVault(b *testing.B) {
    for i := 0; i < b.N; i++ {
        // Test search performance
    }
}
```

### Load Testing

Load tests simulate realistic usage patterns:

- **Concurrent Users**: 10-100
- **Request Rate**: 1-100 requests/second
- **Duration**: 1-10 minutes
- **Metrics**: Response time, throughput, error rate

### Performance Targets

- **Response Time**: < 2 seconds (95th percentile)
- **Throughput**: > 10 requests/second
- **Memory Usage**: < 100MB
- **CPU Usage**: < 50% under load

## Security Testing

### Input Validation

Tests for common security vulnerabilities:

- **SQL Injection**: Malicious SQL in parameters
- **XSS**: Script injection in inputs
- **Path Traversal**: Directory traversal attempts
- **Command Injection**: Shell command injection
- **Null Byte Injection**: Null byte attacks

### Rate Limiting

Tests for rate limiting functionality:

- **Request Rate**: 10-100 requests/second
- **Burst Handling**: Short bursts of high traffic
- **Recovery**: Rate limit reset behavior

### Authentication

Tests for authentication mechanisms:

- **Token Validation**: JWT token verification
- **Permission Checks**: Role-based access control
- **Session Management**: Session handling

## Production Readiness

### Health Checks

Comprehensive health check validation:

- **Server Health**: Basic server status
- **Dependencies**: External service availability
- **Metrics**: Performance metrics
- **Configuration**: Configuration validation

### Monitoring

Monitoring and observability tests:

- **Metrics Collection**: Performance metrics
- **Logging**: Structured logging
- **Alerting**: Error detection
- **Tracing**: Request tracing

### Error Handling

Robust error handling validation:

- **Error Classification**: Error categorization
- **Error Recovery**: Automatic recovery
- **Error Reporting**: Error reporting
- **Graceful Degradation**: Service degradation

## Troubleshooting

### Common Issues

1. **Server Not Running**
   ```bash
   # Start server in mock mode
   go run scripts/working_mcp_server.go -mock=true -port=3011
   ```

2. **Test Timeouts**
   ```bash
   # Increase timeout
   go test -v -timeout 30s ./tests/...
   ```

3. **Port Conflicts**
   ```bash
   # Use different port
   go run scripts/run_all_tests.go 3012
   ```

4. **Dependency Issues**
   ```bash
   # Update dependencies
   go mod tidy
   go mod download
   ```

### Debug Mode

Run tests with debug output:

```bash
# Enable verbose output
go test -v -args -debug

# Enable race detection
go test -v -race ./tests/...

# Enable memory profiling
go test -v -memprofile=mem.prof ./tests/...
```

### Test Coverage

Generate test coverage reports:

```bash
# Generate coverage report
go test -v -cover ./tests/...

# Generate HTML coverage report
go test -v -coverprofile=coverage.out ./tests/...
go tool cover -html=coverage.out -o coverage.html
```

## Best Practices

### Test Design

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Single Responsibility**: One test per scenario
3. **Descriptive Names**: Clear test names
4. **Independent Tests**: Tests should not depend on each other
5. **Cleanup**: Clean up after tests

### Test Data

1. **Mock Data**: Use consistent mock data
2. **Test Fixtures**: Reusable test data
3. **Edge Cases**: Test boundary conditions
4. **Error Cases**: Test error scenarios

### Performance

1. **Parallel Execution**: Run tests in parallel
2. **Resource Cleanup**: Clean up resources
3. **Timeout Handling**: Set appropriate timeouts
4. **Memory Management**: Monitor memory usage

## Continuous Integration

### GitHub Actions

Example CI configuration:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-go@v2
        with:
          go-version: '1.22'
      - run: go mod tidy
      - run: go test -v ./tests/...
```

### Local Development

```bash
# Run tests before commit
make test

# Run specific test category
make test-unit
make test-integration
make test-e2e
```

## Conclusion

This comprehensive testing guide ensures that the MCP server is thoroughly tested across all dimensions:

- **Functionality**: All features work correctly
- **Performance**: Meets performance requirements
- **Security**: Protected against common vulnerabilities
- **Reliability**: Handles errors gracefully
- **Production Ready**: Suitable for production deployment

The test suite provides confidence in the MCP server's quality and reliability, ensuring it meets the highest standards for production use.

---

*Generated by AI Assistant - Data Vault Obsidian Project*  
*MCP Server Testing Guide v1.0.0 - Comprehensive Test Coverage*
