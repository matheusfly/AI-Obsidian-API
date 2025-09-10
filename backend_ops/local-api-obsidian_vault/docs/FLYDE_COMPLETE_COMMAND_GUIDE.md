# 🚀 Flyde Complete Command Guide & Quick Launch

## 📋 Executive Summary

This comprehensive guide provides all Flyde commands, quick launch scripts, and deep conceptual usage patterns for 110% coverage of Flyde's visual programming capabilities.

---

## ⚡ Quick Launch Commands

### 🎯 One-Click Setup & Launch

```bash
# Complete Flyde Environment Setup
curl -fsSL https://raw.githubusercontent.com/flyde-io/flyde/main/scripts/install.sh | bash

# Quick Project Initialization
mkdir flyde-project && cd flyde-project
npm init -y
npm install @flyde/loader @flyde/nodes
npx flyde init

# Launch Flyde Studio
npx flyde studio --port 3001 --open

# Launch with Custom Configuration
npx flyde studio --config ./flyde.config.js --port 3001 --host localhost --open
```

### 🔧 Development Environment Quick Commands

```bash
# Install VS Code Extension (if not already installed)
code --install-extension flyde.flyde-vscode

# Create New Visual Flow
npx flyde create flow my-flow

# Run Flow Directly
npx flyde run my-flow.flyde

# Watch Mode for Development
npx flyde watch my-flow.flyde

# Build for Production
npx flyde build --output dist/

# Test Flow
npx flyde test my-flow.flyde
```

---

## 📚 Complete Command Reference

### 🏗️ Project Management Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `npx flyde init` | Initialize new Flyde project | `npx flyde init my-project` |
| `npx flyde create flow <name>` | Create new visual flow | `npx flyde create flow data-processor` |
| `npx flyde create node <name>` | Create custom node | `npx flyde create node my-custom-node` |
| `npx flyde scaffold` | Generate project structure | `npx flyde scaffold --template full-stack` |

### 🎨 Studio & Development Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx flyde studio` | Launch visual editor | `--port`, `--host`, `--open`, `--config` |
| `npx flyde dev` | Development server | `--watch`, `--hot-reload`, `--debug` |
| `npx flyde watch <flow>` | Watch mode for flow | `--interval 1000`, `--verbose` |
| `npx flyde serve` | Serve flows via HTTP | `--port 3000`, `--cors` |

### 🔄 Flow Execution Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `npx flyde run <flow>` | Execute flow once | `npx flyde run hello-world.flyde` |
| `npx flyde run <flow> --input <data>` | Run with input data | `npx flyde run processor.flyde --input '{"data": "test"}'` |
| `npx flyde run <flow> --output <file>` | Save output to file | `npx flyde run flow.flyde --output result.json` |
| `npx flyde run <flow> --timeout <ms>` | Set execution timeout | `npx flyde run flow.flyde --timeout 5000` |

### 🧪 Testing & Validation Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx flyde test` | Run all tests | `--coverage`, `--watch`, `--verbose` |
| `npx flyde test <flow>` | Test specific flow | `--input`, `--expected-output` |
| `npx flyde validate <flow>` | Validate flow syntax | `--strict`, `--fix` |
| `npx flyde lint` | Lint flows | `--fix`, `--format` |

### 📦 Build & Deployment Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx flyde build` | Build for production | `--output`, `--minify`, `--sourcemap` |
| `npx flyde bundle` | Create deployable bundle | `--target node`, `--target browser` |
| `npx flyde export` | Export flow as code | `--format typescript`, `--format javascript` |
| `npx flyde deploy` | Deploy to cloud | `--target vercel`, `--target aws` |

### 🔍 Debugging & Analysis Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx flyde debug <flow>` | Debug flow execution | `--breakpoints`, `--step-through` |
| `npx flyde trace <flow>` | Trace execution path | `--output trace.json`, `--verbose` |
| `npx flyde profile <flow>` | Performance profiling | `--output profile.json`, `--detailed` |
| `npx flyde analyze <flow>` | Analyze flow complexity | `--metrics`, `--suggestions` |

---

## 🎯 Quick Launch Scripts

### 🚀 Complete Environment Setup Script

```bash
#!/bin/bash
# flyde-quick-setup.sh

echo "🚀 Setting up Flyde Development Environment..."

# Create project directory
PROJECT_NAME=${1:-"flyde-project"}
mkdir -p $PROJECT_NAME && cd $PROJECT_NAME

# Initialize npm project
npm init -y

# Install Flyde dependencies
echo "📦 Installing Flyde dependencies..."
npm install @flyde/loader @flyde/nodes @flyde/runtime

# Install development dependencies
npm install --save-dev @flyde/cli @flyde/studio

# Create basic project structure
mkdir -p flows nodes tests examples

# Create sample flow
cat > flows/hello-world.flyde << 'EOF'
imports: {}
node:
  instances:
    - id: start
      nodeId: InlineValue
      config:
        type: { type: string, value: "string" }
        value: { type: string, value: "Hello, Flyde!" }
    - id: output
      nodeId: Log
      config:
        message: "{{value}}"
  connections:
    - from: { insId: start, pinId: value }
      to: { insId: output, pinId: message
EOF

# Create package.json scripts
cat >> package.json << 'EOF'
  "scripts": {
    "dev": "flyde studio --port 3001 --open",
    "build": "flyde build --output dist/",
    "test": "flyde test",
    "run": "flyde run flows/hello-world.flyde"
  }
EOF

# Create flyde.config.js
cat > flyde.config.js << 'EOF'
module.exports = {
  flowsDir: './flows',
  nodesDir: './nodes',
  outputDir: './dist',
  devServer: {
    port: 3001,
    host: 'localhost',
    open: true
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
EOF

echo "✅ Flyde environment setup complete!"
echo "🎯 Quick commands:"
echo "  npm run dev     - Launch Flyde Studio"
echo "  npm run build   - Build flows"
echo "  npm run test    - Run tests"
echo "  npm run run     - Execute hello-world flow"
```

### 🎨 Studio Launch Scripts

```bash
#!/bin/bash
# flyde-studio-launch.sh

# Default configuration
PORT=${1:-3001}
HOST=${2:-localhost}
CONFIG=${3:-"./flyde.config.js"}

echo "🎨 Launching Flyde Studio..."
echo "📍 Port: $PORT"
echo "🌐 Host: $HOST"
echo "⚙️  Config: $CONFIG"

# Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "⚠️  Config file not found, using defaults"
    npx flyde studio --port $PORT --host $HOST --open
else
    npx flyde studio --config $CONFIG --port $PORT --host $HOST --open
fi
```

### 🔄 Flow Execution Scripts

```bash
#!/bin/bash
# flyde-run-flow.sh

FLOW_FILE=${1:-"flows/hello-world.flyde"}
INPUT_DATA=${2:-'{"message": "Hello from script!"}'}
OUTPUT_FILE=${3:-"output.json"}

echo "🔄 Executing Flow: $FLOW_FILE"
echo "📥 Input: $INPUT_DATA"
echo "📤 Output: $OUTPUT_FILE"

# Run flow with input and save output
npx flyde run $FLOW_FILE --input "$INPUT_DATA" --output $OUTPUT_FILE

echo "✅ Flow execution complete!"
echo "📄 Results saved to: $OUTPUT_FILE"
```

---

## 🧠 Deep Conceptual Usage Guide (110% Coverage)

### 🎯 Core Concepts Mastery

#### 1. Flow Architecture Patterns

**Sequential Processing Pattern:**
```yaml
# flows/sequential-processing.flyde
imports:
  utils: "@flyde/nodes"

node:
  instances:
    - id: input-processor
      nodeId: DataProcessor
      config:
        operation: "validate"
    - id: transformer
      nodeId: DataTransformer
      config:
        rules: ["normalize", "enrich"]
    - id: output-generator
      nodeId: OutputGenerator
      config:
        format: "json"
  
  connections:
    - from: { insId: input-processor, pinId: output }
      to: { insId: transformer, pinId: input }
    - from: { insId: transformer, pinId: output }
      to: { insId: output-generator, pinId: input }
```

**Parallel Processing Pattern:**
```yaml
# flows/parallel-processing.flyde
imports:
  async: "@flyde/nodes"

node:
  instances:
    - id: input-splitter
      nodeId: DataSplitter
      config:
        strategy: "round-robin"
    - id: processor-1
      nodeId: DataProcessor
      config:
        id: "processor-1"
    - id: processor-2
      nodeId: DataProcessor
      config:
        id: "processor-2"
    - id: processor-3
      nodeId: DataProcessor
      config:
        id: "processor-3"
    - id: result-merger
      nodeId: ResultMerger
      config:
        strategy: "combine"
  
  connections:
    - from: { insId: input-splitter, pinId: output-1 }
      to: { insId: processor-1, pinId: input }
    - from: { insId: input-splitter, pinId: output-2 }
      to: { insId: processor-2, pinId: input }
    - from: { insId: input-splitter, pinId: output-3 }
      to: { insId: processor-3, pinId: input }
    - from: { insId: processor-1, pinId: output }
      to: { insId: result-merger, pinId: input-1 }
    - from: { insId: processor-2, pinId: output }
      to: { insId: result-merger, pinId: input-2 }
    - from: { insId: processor-3, pinId: output }
      to: { insId: result-merger, pinId: input-3 }
```

**Conditional Branching Pattern:**
```yaml
# flows/conditional-branching.flyde
imports:
  logic: "@flyde/nodes"

node:
  instances:
    - id: input-analyzer
      nodeId: InputAnalyzer
      config:
        criteria: ["type", "priority", "source"]
    - id: condition-checker
      nodeId: ConditionChecker
      config:
        conditions:
          - field: "type"
            operator: "equals"
            value: "urgent"
          - field: "priority"
            operator: "greater_than"
            value: 7
    - id: urgent-processor
      nodeId: UrgentProcessor
      config:
        timeout: 1000
    - id: normal-processor
      nodeId: NormalProcessor
      config:
        timeout: 5000
    - id: result-router
      nodeId: ResultRouter
      config:
        routing_strategy: "merge"
  
  connections:
    - from: { insId: input-analyzer, pinId: output }
      to: { insId: condition-checker, pinId: input }
    - from: { insId: condition-checker, pinId: true }
      to: { insId: urgent-processor, pinId: input }
    - from: { insId: condition-checker, pinId: false }
      to: { insId: normal-processor, pinId: input }
    - from: { insId: urgent-processor, pinId: output }
      to: { insId: result-router, pinId: urgent-input }
    - from: { insId: normal-processor, pinId: output }
      to: { insId: result-router, pinId: normal-input }
```

#### 2. Advanced Node Development

**Custom Node with TypeScript:**
```typescript
// nodes/ai-processor.ts
import { NodeDefinition, NodeInstance } from '@flyde/core'

export const AiProcessorNode: NodeDefinition = {
  id: 'AiProcessor',
  displayName: 'AI Processor',
  description: 'Processes data using AI models',
  
  inputs: {
    input: {
      type: 'string',
      description: 'Input data to process'
    },
    model: {
      type: 'string',
      description: 'AI model to use',
      defaultValue: 'gpt-4o-mini'
    },
    prompt: {
      type: 'string',
      description: 'Processing prompt'
    }
  },
  
  outputs: {
    result: {
      type: 'string',
      description: 'AI processing result'
    },
    confidence: {
      type: 'number',
      description: 'Confidence score'
    },
    error: {
      type: 'string',
      description: 'Error message if any'
    }
  },
  
  async execute(inputs, { logger }) {
    try {
      logger.info('Starting AI processing', { model: inputs.model })
      
      // AI processing logic
      const result = await processWithAI({
        input: inputs.input,
        model: inputs.model,
        prompt: inputs.prompt
      })
      
      return {
        result: result.text,
        confidence: result.confidence
      }
    } catch (error) {
      logger.error('AI processing failed', { error })
      return {
        error: error.message
      }
    }
  }
}
```

**Async Node with Promise Handling:**
```typescript
// nodes/async-data-fetcher.ts
export const AsyncDataFetcherNode: NodeDefinition = {
  id: 'AsyncDataFetcher',
  displayName: 'Async Data Fetcher',
  description: 'Fetches data asynchronously with retry logic',
  
  inputs: {
    url: { type: 'string' },
    retries: { type: 'number', defaultValue: 3 },
    timeout: { type: 'number', defaultValue: 5000 }
  },
  
  outputs: {
    data: { type: 'object' },
    status: { type: 'number' },
    error: { type: 'string' }
  },
  
  async execute(inputs, { logger }) {
    const { url, retries, timeout } = inputs
    
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        logger.info(`Fetching data (attempt ${attempt}/${retries})`, { url })
        
        const response = await fetch(url, {
          signal: AbortSignal.timeout(timeout)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        return {
          data,
          status: response.status
        }
      } catch (error) {
        logger.warn(`Attempt ${attempt} failed`, { error: error.message })
        
        if (attempt === retries) {
          return {
            error: `Failed after ${retries} attempts: ${error.message}`
          }
        }
        
        // Exponential backoff
        await new Promise(resolve => 
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        )
      }
    }
  }
}
```

#### 3. Integration Patterns

**HTTP API Integration:**
```yaml
# flows/api-integration.flyde
imports:
  http: "@flyde/nodes"
  auth: "@flyde/nodes"

node:
  instances:
    - id: auth-manager
      nodeId: AuthManager
      config:
        type: "bearer"
        token: "${API_TOKEN}"
    - id: request-builder
      nodeId: RequestBuilder
      config:
        base_url: "https://api.example.com"
        headers:
          Content-Type: "application/json"
    - id: api-caller
      nodeId: HTTPRequest
      config:
        method: "POST"
        timeout: 10000
    - id: response-processor
      nodeId: ResponseProcessor
      config:
        success_codes: [200, 201]
        error_handling: "retry"
  
  connections:
    - from: { insId: auth-manager, pinId: token }
      to: { insId: request-builder, pinId: auth_header }
    - from: { insId: request-builder, pinId: request }
      to: { insId: api-caller, pinId: request }
    - from: { insId: api-caller, pinId: response }
      to: { insId: response-processor, pinId: response }
```

**Database Integration:**
```yaml
# flows/database-integration.flyde
imports:
  db: "@flyde/nodes"

node:
  instances:
    - id: db-connector
      nodeId: DatabaseConnector
      config:
        type: "postgresql"
        connection_string: "${DATABASE_URL}"
        pool_size: 10
    - id: query-builder
      nodeId: QueryBuilder
      config:
        dialect: "postgresql"
        validation: true
    - id: query-executor
      nodeId: QueryExecutor
      config:
        timeout: 30000
        retries: 3
    - id: result-formatter
      nodeId: ResultFormatter
      config:
        format: "json"
        include_metadata: true
  
  connections:
    - from: { insId: db-connector, pinId: connection }
      to: { insId: query-executor, pinId: connection }
    - from: { insId: query-builder, pinId: query }
      to: { insId: query-executor, pinId: query }
    - from: { insId: query-executor, pinId: result }
      to: { insId: result-formatter, pinId: data }
```

#### 4. Error Handling & Resilience

**Comprehensive Error Handling:**
```yaml
# flows/error-handling.flyde
imports:
  error: "@flyde/nodes"
  retry: "@flyde/nodes"

node:
  instances:
    - id: input-validator
      nodeId: InputValidator
      config:
        schema: "strict"
        required_fields: ["id", "data"]
    - id: retry-handler
      nodeId: RetryHandler
      config:
        max_retries: 3
        backoff_strategy: "exponential"
        retry_conditions: ["timeout", "network_error"]
    - id: error-classifier
      nodeId: ErrorClassifier
      config:
        categories:
          - name: "recoverable"
            patterns: ["timeout", "rate_limit"]
          - name: "fatal"
            patterns: ["auth_error", "validation_error"]
    - id: error-handler
      nodeId: ErrorHandler
      config:
        strategies:
          recoverable: "retry"
          fatal: "log_and_fail"
    - id: fallback-processor
      nodeId: FallbackProcessor
      config:
        fallback_data: "default_value"
  
  connections:
    - from: { insId: input-validator, pinId: valid }
      to: { insId: retry-handler, pinId: input }
    - from: { insId: input-validator, pinId: invalid }
      to: { insId: error-classifier, pinId: error }
    - from: { insId: retry-handler, pinId: success }
      to: { insId: output, pinId: result }
    - from: { insId: retry-handler, pinId: failed }
      to: { insId: error-classifier, pinId: error }
    - from: { insId: error-classifier, pinId: recoverable }
      to: { insId: retry-handler, pinId: retry }
    - from: { insId: error-classifier, pinId: fatal }
      to: { insId: fallback-processor, pinId: input }
```

#### 5. Performance Optimization

**Caching & Optimization:**
```yaml
# flows/performance-optimized.flyde
imports:
  cache: "@flyde/nodes"
  batch: "@flyde/nodes"

node:
  instances:
    - id: cache-manager
      nodeId: CacheManager
      config:
        type: "redis"
        ttl: 3600
        max_size: 1000
    - id: batch-processor
      nodeId: BatchProcessor
      config:
        batch_size: 100
        flush_interval: 5000
        max_wait_time: 10000
    - id: parallel-executor
      nodeId: ParallelExecutor
      config:
        max_concurrent: 10
        queue_size: 1000
    - id: memory-optimizer
      nodeId: MemoryOptimizer
      config:
        gc_threshold: 0.8
        compression: true
    - id: performance-monitor
      nodeId: PerformanceMonitor
      config:
        metrics: ["execution_time", "memory_usage", "throughput"]
        alert_thresholds:
          execution_time: 5000
          memory_usage: 0.9
  
  connections:
    - from: { insId: input, pinId: data }
      to: { insId: cache-manager, pinId: check }
    - from: { insId: cache-manager, pinId: miss }
      to: { insId: batch-processor, pinId: input }
    - from: { insId: batch-processor, pinId: batch }
      to: { insId: parallel-executor, pinId: tasks }
    - from: { insId: parallel-executor, pinId: results }
      to: { insId: cache-manager, pinId: store }
```

---

## 🎯 Advanced Usage Patterns

### 🔄 Real-time Data Processing

```yaml
# flows/realtime-processing.flyde
imports:
  stream: "@flyde/nodes"
  websocket: "@flyde/nodes"

node:
  instances:
    - id: websocket-client
      nodeId: WebSocketClient
      config:
        url: "wss://api.example.com/stream"
        protocols: ["json-stream"]
        reconnect: true
        max_reconnect_attempts: 10
    - id: stream-processor
      nodeId: StreamProcessor
      config:
        buffer_size: 1000
        processing_interval: 100
        batch_size: 50
    - id: real-time-analyzer
      nodeId: RealTimeAnalyzer
      config:
        window_size: 1000
        analysis_types: ["trend", "anomaly", "pattern"]
    - id: alert-manager
      nodeId: AlertManager
      config:
        thresholds:
          anomaly_score: 0.8
          trend_change: 0.5
        notification_channels: ["email", "slack", "webhook"]
```

### 🤖 AI Integration Patterns

```yaml
# flows/ai-integration.flyde
imports:
  ai: "@flyde/nodes"
  llm: "@flyde/nodes"

node:
  instances:
    - id: model-selector
      nodeId: ModelSelector
      config:
        models:
          - name: "gpt-4o"
            use_case: "complex_reasoning"
            cost: "high"
          - name: "gpt-4o-mini"
            use_case: "simple_tasks"
            cost: "low"
          - name: "claude-3-sonnet"
            use_case: "analysis"
            cost: "medium"
    - id: prompt-optimizer
      nodeId: PromptOptimizer
      config:
        optimization_strategies: ["few_shot", "chain_of_thought", "self_consistency"]
    - id: response-validator
      nodeId: ResponseValidator
      config:
        validation_criteria:
          - "completeness"
          - "accuracy"
          - "relevance"
        confidence_threshold: 0.8
    - id: result-aggregator
      nodeId: ResultAggregator
      config:
        aggregation_method: "weighted_average"
        weights:
          gpt-4o: 0.4
          claude-3-sonnet: 0.4
          gpt-4o-mini: 0.2
```

---

## 🚀 Production Deployment Commands

### 🐳 Docker Deployment

```bash
# Build Flyde Docker image
docker build -t flyde-app:latest .

# Run with Docker Compose
docker-compose up -d

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### ☁️ Cloud Deployment

```bash
# Deploy to Vercel
npx flyde deploy --target vercel --env production

# Deploy to AWS Lambda
npx flyde deploy --target aws-lambda --region us-east-1

# Deploy to Google Cloud Functions
npx flyde deploy --target gcp-functions --region us-central1
```

---

## 📊 Monitoring & Analytics Commands

```bash
# Performance monitoring
npx flyde monitor --metrics cpu,memory,execution-time

# Flow analytics
npx flyde analyze flows/ --output analytics.json

# Health check
npx flyde health-check --endpoint http://localhost:3001

# Generate performance report
npx flyde report --format html --output performance-report.html
```

This comprehensive guide provides 110% coverage of Flyde's capabilities, from basic commands to advanced patterns and production deployment strategies.
