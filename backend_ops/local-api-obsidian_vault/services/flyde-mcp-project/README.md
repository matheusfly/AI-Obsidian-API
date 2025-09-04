# 🚀 Flyde MCP Project - Visual Programming with AI Agents

A comprehensive collection of Flyde visual programming examples, powered by MCP (Model Context Protocol) tools for enhanced AI agent workflows.

## 🌟 What is Flyde?

Flyde is a visual, flow-based programming toolkit that **integrates with your existing code**. It allows you to create and run visual programs using TypeScript/JavaScript, perfect for building AI agent workflows and complex business logic.

### Key Features:
- **Visual Flow Programming**: Create complex workflows using drag-and-drop interface
- **TypeScript Integration**: Seamlessly integrates with existing codebases
- **AI Agent Ready**: Perfect for building agentic workflows and AI systems
- **Real-time Execution**: See your flows execute in real-time with visual debugging
- **Custom Nodes**: Create reusable components for your specific needs

## 🎯 Project Structure

```
flyde-mcp-project/
├── examples/           # Interactive Flyde examples
│   ├── hello-world/    # Basic hello world flow
│   ├── ai-agent/       # AI agent workflow example
│   ├── data-pipeline/  # Data processing pipeline
│   └── api-integration/ # API integration flows
├── src/               # Source code and utilities
├── docs/              # Documentation and guides
└── flows/             # Reusable Flyde flow files
```

## 🚀 Quick Start

### 1. Installation

```bash
npm install
```

### 2. Run Examples

#### 🌐 **INTERACTIVE WEB UI** (RECOMMENDED)
```bash
# Start the interactive web interface
npm run ui

# Then open your browser to:
# http://localhost:3000
```

#### 💻 **Command Line Interface**
```bash
# 🚀 Run the MCP playground (FULLY WORKING)
npm run mcp-playground

# Run Sentry MCP demo
npm run sentry-demo

# Run with Sentry monitoring
npm run sentry-playground

# Run original playground (Flyde format issues)
npm run playground

# Start the development server
npm run dev
```

### 🎯 **WORKING EXAMPLES** ✅

The following examples are **fully functional** with complete Sentry MCP monitoring:

- **`npm run ui`** - 🌟 **INTERACTIVE WEB UI** - Visual interface with real-time monitoring
- **`npm run mcp-playground`** - 💻 **COMMAND LINE** - Full MCP functionality
- **`npm run sentry-demo`** - Pure Sentry MCP integration demo  
- **`npm run sentry-playground`** - Enhanced monitoring playground

### 3. Explore Flows

Each example includes:
- **Visual Flow** (`.flyde` files)
- **TypeScript Integration** (`.ts` files)
- **Custom Nodes** (when needed)
- **Documentation** and usage examples

## 📚 Examples Included

### 1. Hello World Flow
- **File**: `examples/hello-world/`
- **Description**: Basic introduction to Flyde concepts
- **Features**: Simple data flow, input/output handling
- **Perfect for**: Learning Flyde basics

### 2. AI Agent Workflow
- **File**: `examples/ai-agent/`
- **Description**: Complete AI agent implementation
- **Features**: 
  - Input processing
  - AI model integration
  - Response formatting
  - Error handling
- **Perfect for**: Building AI-powered applications

### 3. Data Pipeline
- **File**: `examples/data-pipeline/`
- **Description**: ETL pipeline with visual flows
- **Features**:
  - Data transformation
  - Validation steps
  - Error handling
  - Progress tracking
- **Perfect for**: Data processing workflows

### 4. API Integration
- **File**: `examples/api-integration/`
- **Description**: REST API integration patterns
- **Features**:
  - HTTP requests
  - Response processing
  - Authentication
  - Rate limiting
- **Perfect for**: Microservices and API workflows

### 5. Sentry Monitoring
- **File**: `examples/sentry-monitored-flow/`
- **Description**: Sentry MCP integration for monitoring
- **Features**:
  - Real-time error tracking
  - Performance monitoring
  - Flow execution logging
  - Automatic alerting
- **Perfect for**: Production monitoring and debugging

## 🛠 MCP Integration

This project leverages MCP (Model Context Protocol) tools for enhanced functionality:

- **Web Crawling**: Automated documentation fetching
- **Code Generation**: AI-powered flow creation
- **Real-time Monitoring**: Live flow execution tracking
- **Interactive Demos**: Browser-based playground

## 🎨 Visual Programming Benefits

### Why Use Flyde for AI Agents?

1. **Visual Clarity**: See your agent's logic flow at a glance
2. **Easy Debugging**: Visual execution makes issues obvious
3. **Team Collaboration**: Non-technical team members can understand flows
4. **Rapid Iteration**: Modify flows without deep code changes
5. **Integration**: Works seamlessly with existing TypeScript code

### Core Concepts

- **Nodes**: Individual processing units with inputs/outputs
- **Connections**: Wires that pass data between nodes
- **Flows**: Complete programs made of connected nodes
- **Custom Nodes**: Reusable components for specific functionality

## 🔧 Development

### Creating New Flows

1. Use the VSCode extension: `Flyde: New visual flow`
2. Design your flow visually
3. Integrate with TypeScript code using `@flyde/loader`
4. Test and iterate

### Custom Nodes

Create reusable components:

```typescript
import { CodeNode } from '@flyde/core';

export const MyCustomNode: CodeNode = {
  id: 'MyCustomNode',
  displayName: 'My Custom Node',
  description: 'Does something awesome',
  inputs: {
    input: { description: 'Input value' }
  },
  outputs: {
    result: { description: 'Processed result' }
  },
  run: (inputs, outputs) => {
    // Your custom logic here
    outputs.result.next(inputs.input * 2);
  }
};
```

## 📖 Documentation

- [Flyde Official Docs](https://flyde.dev/docs)
- [Core Concepts](./docs/core-concepts.md)
- [API Reference](./docs/api-reference.md)
- [Best Practices](./docs/best-practices.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🌐 Live Demos

- [Online Playground](https://flyde.dev/playground)
- [Interactive Examples](./examples/)
- [Video Tutorials](./docs/videos/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your example or improvement
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- [Discord Community](https://www.flyde.dev/discord)
- [GitHub Issues](https://github.com/flydelabs/flyde/issues)
- [Documentation](https://flyde.dev/docs)

---

**Built with ❤️ using Flyde and MCP tools**

*Visual programming for the AI era*