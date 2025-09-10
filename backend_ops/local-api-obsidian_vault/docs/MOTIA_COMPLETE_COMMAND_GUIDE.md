# ⚡ Motia Complete Command Guide & Quick Launch

## 📋 Executive Summary

This comprehensive guide provides all Motia commands, quick launch scripts, and deep conceptual usage patterns for 110% coverage of Motia's workflow automation capabilities.

---

## ⚡ Quick Launch Commands

### 🎯 One-Click Setup & Launch

```bash
# Complete Motia Environment Setup
npx create-motia-app@latest my-motia-app
cd my-motia-app
npm install
npm run dev

# Quick Project Initialization
mkdir motia-project && cd motia-project
npm init -y
npm install motia
npx motia init

# Launch Motia Development Server
npx motia dev --port 3000 --open

# Launch with Custom Configuration
npx motia dev --config ./motia.config.js --port 3000 --host localhost --open
```

### 🔧 Development Environment Quick Commands

```bash
# Create New Step
npx motia create step my-step

# Create New Workflow
npx motia create workflow my-workflow

# Run Step Directly
npx motia run steps/my-step.step.ts

# Watch Mode for Development
npx motia watch steps/

# Build for Production
npx motia build --output dist/

# Test Steps
npx motia test steps/
```

---

## 📚 Complete Command Reference

### 🏗️ Project Management Commands

| Command | Description | Usage Example |
|---------|-------------|---------------|
| `npx motia init` | Initialize new Motia project | `npx motia init my-project` |
| `npx motia create step <name>` | Create new step | `npx motia create step data-processor` |
| `npx motia create workflow <name>` | Create new workflow | `npx motia create workflow api-gateway` |
| `npx motia scaffold` | Generate project structure | `npx motia scaffold --template full-stack` |

### 🎨 Development Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx motia dev` | Launch development server | `--port`, `--host`, `--open`, `--config` |
| `npx motia watch <path>` | Watch mode for files | `--interval 1000`, `--verbose` |
| `npx motia serve` | Serve workflows via HTTP | `--port 3000`, `--cors` |
| `npx motia workbench` | Launch visual workbench | `--port 3001`, `--open` |

### 🔄 Step Execution Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `npx motia run <step>` | Execute step once | `npx motia run steps/api.step.ts` |
| `npx motia run <step> --input <data>` | Run with input data | `npx motia run step.ts --input '{"data": "test"}'` |
| `npx motia run <step> --output <file>` | Save output to file | `npx motia run step.ts --output result.json` |
| `npx motia run <step> --timeout <ms>` | Set execution timeout | `npx motia run step.ts --timeout 5000` |

### 🧪 Testing & Validation Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx motia test` | Run all tests | `--coverage`, `--watch`, `--verbose` |
| `npx motia test <step>` | Test specific step | `--input`, `--expected-output` |
| `npx motia validate <step>` | Validate step syntax | `--strict`, `--fix` |
| `npx motia lint` | Lint steps | `--fix`, `--format` |

### 📦 Build & Deployment Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx motia build` | Build for production | `--output`, `--minify`, `--sourcemap` |
| `npx motia bundle` | Create deployable bundle | `--target node`, `--target serverless` |
| `npx motia export` | Export workflow as code | `--format typescript`, `--format javascript` |
| `npx motia deploy` | Deploy to cloud | `--target vercel`, `--target aws` |

### 🔍 Debugging & Analysis Commands

| Command | Description | Options |
|---------|-------------|---------|
| `npx motia debug <step>` | Debug step execution | `--breakpoints`, `--step-through` |
| `npx motia trace <step>` | Trace execution path | `--output trace.json`, `--verbose` |
| `npx motia profile <step>` | Performance profiling | `--output profile.json`, `--detailed` |
| `npx motia analyze <step>` | Analyze step complexity | `--metrics`, `--suggestions` |

---

## 🎯 Quick Launch Scripts

### 🚀 Complete Environment Setup Script

```bash
#!/bin/bash
# motia-quick-setup.sh

echo "⚡ Setting up Motia Development Environment..."

# Create project directory
PROJECT_NAME=${1:-"motia-project"}
mkdir -p $PROJECT_NAME && cd $PROJECT_NAME

# Initialize npm project
npm init -y

# Install Motia dependencies
echo "📦 Installing Motia dependencies..."
npm install motia

# Install development dependencies
npm install --save-dev @types/node typescript ts-node

# Create basic project structure
mkdir -p steps workflows tests examples

# Create sample step
cat > steps/hello-world.step.ts << 'EOF'
import { StepConfig, Handlers } from 'motia'

export const config: StepConfig = {
  type: 'api',
  name: 'HelloWorld',
  description: 'Simple hello world step',
  method: 'GET',
  path: '/hello',
  responseSchema: {
    200: {
      type: 'object',
      properties: {
        message: { type: 'string' },
        timestamp: { type: 'string' }
      }
    }
  }
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger }) => {
  logger.info('Hello World step executed')
  
  return {
    status: 200,
    body: {
      message: 'Hello, Motia!',
      timestamp: new Date().toISOString()
    }
  }
}
EOF

# Create package.json scripts
cat >> package.json << 'EOF'
  "scripts": {
    "dev": "motia dev --port 3000 --open",
    "build": "motia build --output dist/",
    "test": "motia test",
    "run": "motia run steps/hello-world.step.ts"
  }
EOF

# Create motia.config.js
cat > motia.config.js << 'EOF'
module.exports = {
  stepsDir: './steps',
  workflowsDir: './workflows',
  outputDir: './dist',
  devServer: {
    port: 3000,
    host: 'localhost',
    open: true
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
EOF

echo "✅ Motia environment setup complete!"
echo "🎯 Quick commands:"
echo "  npm run dev     - Launch Motia Dev Server"
echo "  npm run build   - Build steps"
echo "  npm run test    - Run tests"
echo "  npm run run     - Execute hello-world step"
```

### 🎨 Development Server Launch Script

```bash
#!/bin/bash
# motia-dev-launch.sh

# Default configuration
PORT=${1:-3000}
HOST=${2:-localhost}
CONFIG=${3:-"./motia.config.js"}

echo "⚡ Launching Motia Development Server..."
echo "📍 Port: $PORT"
echo "🌐 Host: $HOST"
echo "⚙️  Config: $CONFIG"

# Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "⚠️  Config file not found, using defaults"
    npx motia dev --port $PORT --host $HOST --open
else
    npx motia dev --config $CONFIG --port $PORT --host $HOST --open
fi
```

### 🔄 Step Execution Script

```bash
#!/bin/bash
# motia-run-step.sh

STEP_FILE=${1:-"steps/hello-world.step.ts"}
INPUT_DATA=${2:-'{"message": "Hello from script!"}'}
OUTPUT_FILE=${3:-"output.json"}

echo "🔄 Executing Step: $STEP_FILE"
echo "📥 Input: $INPUT_DATA"
echo "📤 Output: $OUTPUT_FILE"

# Run step with input and save output
npx motia run $STEP_FILE --input "$INPUT_DATA" --output $OUTPUT_FILE

echo "✅ Step execution complete!"
echo "📄 Results saved to: $OUTPUT_FILE"
```

---

## 🧠 Deep Conceptual Usage Guide (110% Coverage)

### 🎯 Core Concepts Mastery

#### 1. Step Architecture Patterns

**API Route Pattern:**
```typescript
// steps/api-route.step.ts
import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'DataProcessor',
  description: 'Process incoming data via API',
  method: 'POST',
  path: '/api/process',
  bodySchema: z.object({
    data: z.string(),
    options: z.object({
      format: z.enum(['json', 'xml', 'csv']),
      validate: z.boolean().default(true)
    }).optional()
  }),
  responseSchema: {
    200: z.object({
      success: z.boolean(),
      result: z.any(),
      processingTime: z.number()
    }),
    400: z.object({
      error: z.string(),
      details: z.any()
    })
  },
  emits: ['data-processed', 'validation-failed']
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger, emit }) => {
  const startTime = Date.now()
  
  try {
    logger.info('Processing data request', { 
      dataLength: req.body.data.length,
      format: req.body.options?.format 
    })
    
    // Process data
    const result = await processData(req.body.data, req.body.options)
    
    // Emit event
    await emit({
      topic: 'data-processed',
      data: {
        result,
        processingTime: Date.now() - startTime
      }
    })
    
    return {
      status: 200,
      body: {
        success: true,
        result,
        processingTime: Date.now() - startTime
      }
    }
  } catch (error) {
    logger.error('Data processing failed', { error: error.message })
    
    await emit({
      topic: 'validation-failed',
      data: {
        error: error.message,
        input: req.body
      }
    })
    
    return {
      status: 400,
      body: {
        error: 'Processing failed',
        details: error.message
      }
    }
  }
}
```

**Cron Job Pattern:**
```typescript
// steps/cron-job.step.ts
import { CronJobConfig, Handlers } from 'motia'

export const config: CronJobConfig = {
  type: 'cron',
  name: 'DataCleanup',
  description: 'Clean up old data every hour',
  schedule: '0 * * * *', // Every hour
  timezone: 'UTC',
  emits: ['cleanup-started', 'cleanup-completed', 'cleanup-failed']
}

export const handler: Handlers['CronJob'] = async (context, { logger, emit }) => {
  logger.info('Starting data cleanup job')
  
  try {
    await emit({
      topic: 'cleanup-started',
      data: {
        timestamp: new Date().toISOString(),
        jobId: context.jobId
      }
    })
    
    // Cleanup logic
    const deletedCount = await cleanupOldData()
    
    await emit({
      topic: 'cleanup-completed',
      data: {
        deletedCount,
        timestamp: new Date().toISOString()
      }
    })
    
    logger.info('Data cleanup completed', { deletedCount })
  } catch (error) {
    logger.error('Data cleanup failed', { error: error.message })
    
    await emit({
      topic: 'cleanup-failed',
      data: {
        error: error.message,
        timestamp: new Date().toISOString()
      }
    })
  }
}
```

**Stream Processing Pattern:**
```typescript
// steps/stream-processor.step.ts
import { StreamConfig, Handlers } from 'motia'

export const config: StreamConfig = {
  type: 'stream',
  name: 'RealTimeProcessor',
  description: 'Process real-time data streams',
  streamSource: 'kafka',
  topics: ['user-events', 'system-metrics'],
  emits: ['event-processed', 'anomaly-detected', 'batch-completed']
}

export const handler: Handlers['StreamProcessor'] = async (event, context, { logger, emit }) => {
  logger.info('Processing stream event', { 
    eventType: event.type,
    topic: event.topic 
  })
  
  try {
    // Process event
    const result = await processEvent(event)
    
    // Check for anomalies
    if (result.anomalyScore > 0.8) {
      await emit({
        topic: 'anomaly-detected',
        data: {
          event,
          anomalyScore: result.anomalyScore,
          timestamp: new Date().toISOString()
        }
      })
    }
    
    await emit({
      topic: 'event-processed',
      data: {
        eventId: event.id,
        result,
        processingTime: result.processingTime
      }
    })
    
  } catch (error) {
    logger.error('Stream processing failed', { 
      error: error.message,
      eventId: event.id 
    })
  }
}
```

#### 2. Advanced Step Development

**Custom Step with TypeScript:**
```typescript
// steps/ai-processor.step.ts
import { StepConfig, Handlers } from 'motia'
import { z } from 'zod'

interface AIProcessorConfig extends StepConfig {
  aiModel: string
  maxTokens: number
  temperature: number
}

export const config: AIProcessorConfig = {
  type: 'api',
  name: 'AIProcessor',
  description: 'Process data using AI models',
  method: 'POST',
  path: '/api/ai/process',
  aiModel: 'gpt-4o-mini',
  maxTokens: 1000,
  temperature: 0.7,
  bodySchema: z.object({
    prompt: z.string(),
    context: z.any().optional(),
    options: z.object({
      model: z.string().optional(),
      maxTokens: z.number().optional(),
      temperature: z.number().optional()
    }).optional()
  }),
  responseSchema: {
    200: z.object({
      result: z.string(),
      confidence: z.number(),
      tokensUsed: z.number()
    })
  },
  emits: ['ai-processing-started', 'ai-processing-completed']
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger, emit }) => {
  const { prompt, context, options } = req.body
  
  try {
    await emit({
      topic: 'ai-processing-started',
      data: {
        prompt: prompt.substring(0, 100),
        model: options?.model || config.aiModel
      }
    })
    
    logger.info('Starting AI processing', { 
      model: options?.model || config.aiModel,
      promptLength: prompt.length 
    })
    
    // AI processing logic
    const result = await processWithAI({
      prompt,
      context,
      model: options?.model || config.aiModel,
      maxTokens: options?.maxTokens || config.maxTokens,
      temperature: options?.temperature || config.temperature
    })
    
    await emit({
      topic: 'ai-processing-completed',
      data: {
        result: result.text,
        confidence: result.confidence,
        tokensUsed: result.tokensUsed
      }
    })
    
    return {
      status: 200,
      body: {
        result: result.text,
        confidence: result.confidence,
        tokensUsed: result.tokensUsed
      }
    }
  } catch (error) {
    logger.error('AI processing failed', { error: error.message })
    
    return {
      status: 500,
      body: {
        error: 'AI processing failed',
        details: error.message
      }
    }
  }
}
```

#### 3. Integration Patterns

**Database Integration:**
```typescript
// steps/database-integration.step.ts
import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'DatabaseManager',
  description: 'Manage database operations',
  method: 'POST',
  path: '/api/db/query',
  bodySchema: z.object({
    operation: z.enum(['select', 'insert', 'update', 'delete']),
    table: z.string(),
    data: z.any().optional(),
    where: z.any().optional(),
    limit: z.number().optional()
  }),
  responseSchema: {
    200: z.object({
      success: z.boolean(),
      data: z.any(),
      affectedRows: z.number().optional()
    })
  },
  emits: ['db-query-executed', 'db-error']
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger, emit }) => {
  const { operation, table, data, where, limit } = req.body
  
  try {
    logger.info('Executing database operation', { operation, table })
    
    const result = await executeDatabaseOperation({
      operation,
      table,
      data,
      where,
      limit
    })
    
    await emit({
      topic: 'db-query-executed',
      data: {
        operation,
        table,
        affectedRows: result.affectedRows,
        executionTime: result.executionTime
      }
    })
    
    return {
      status: 200,
      body: {
        success: true,
        data: result.data,
        affectedRows: result.affectedRows
      }
    }
  } catch (error) {
    logger.error('Database operation failed', { error: error.message })
    
    await emit({
      topic: 'db-error',
      data: {
        operation,
        table,
        error: error.message
      }
    })
    
    return {
      status: 500,
      body: {
        success: false,
        error: 'Database operation failed',
        details: error.message
      }
    }
  }
}
```

**External API Integration:**
```typescript
// steps/external-api.step.ts
import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'ExternalAPIGateway',
  description: 'Gateway for external API calls',
  method: 'POST',
  path: '/api/external/call',
  bodySchema: z.object({
    service: z.string(),
    endpoint: z.string(),
    method: z.enum(['GET', 'POST', 'PUT', 'DELETE']),
    data: z.any().optional(),
    headers: z.record(z.string()).optional(),
    timeout: z.number().default(10000)
  }),
  responseSchema: {
    200: z.object({
      success: z.boolean(),
      data: z.any(),
      statusCode: z.number(),
      responseTime: z.number()
    })
  },
  emits: ['external-api-called', 'external-api-error']
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger, emit }) => {
  const { service, endpoint, method, data, headers, timeout } = req.body
  
  try {
    const startTime = Date.now()
    
    logger.info('Calling external API', { service, endpoint, method })
    
    const response = await callExternalAPI({
      service,
      endpoint,
      method,
      data,
      headers,
      timeout
    })
    
    const responseTime = Date.now() - startTime
    
    await emit({
      topic: 'external-api-called',
      data: {
        service,
        endpoint,
        method,
        statusCode: response.status,
        responseTime
      }
    })
    
    return {
      status: 200,
      body: {
        success: true,
        data: response.data,
        statusCode: response.status,
        responseTime
      }
    }
  } catch (error) {
    logger.error('External API call failed', { 
      error: error.message,
      service,
      endpoint 
    })
    
    await emit({
      topic: 'external-api-error',
      data: {
        service,
        endpoint,
        error: error.message
      }
    })
    
    return {
      status: 500,
      body: {
        success: false,
        error: 'External API call failed',
        details: error.message
      }
    }
  }
}
```

---

## 🚀 Production Deployment Commands

### 🐳 Docker Deployment

```bash
# Build Motia Docker image
docker build -t motia-app:latest .

# Run with Docker Compose
docker-compose up -d

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### ☁️ Cloud Deployment

```bash
# Deploy to Vercel
npx motia deploy --target vercel --env production

# Deploy to AWS Lambda
npx motia deploy --target aws-lambda --region us-east-1

# Deploy to Google Cloud Functions
npx motia deploy --target gcp-functions --region us-central1
```

---

## 📊 Monitoring & Analytics Commands

```bash
# Performance monitoring
npx motia monitor --metrics cpu,memory,execution-time

# Step analytics
npx motia analyze steps/ --output analytics.json

# Health check
npx motia health-check --endpoint http://localhost:3000

# Generate performance report
npx motia report --format html --output performance-report.html
```

This comprehensive guide provides 110% coverage of Motia's capabilities, from basic commands to advanced patterns and production deployment strategies.
