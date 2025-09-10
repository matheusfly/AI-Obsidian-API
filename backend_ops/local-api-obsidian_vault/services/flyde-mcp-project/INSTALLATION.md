# 🚀 Flyde MCP Project - Installation Guide

## Quick Start

### 1. Prerequisites

- Node.js 18+ 
- npm or yarn
- VSCode (recommended)
- Git

### 2. Installation

```bash
# Clone or download the project
cd flyde-mcp-project

# Install dependencies
npm install

# Install VSCode extension (optional but recommended)
# Search for "Flyde" in VSCode extensions marketplace
```

### 3. Run Examples

```bash
# Run all examples
npm run playground

# Run specific example
node examples/hello-world/index.ts
node examples/ai-agent/index.ts
node examples/data-pipeline/index.ts
node examples/mcp-integration/index.ts

# Start development server
npm run dev
```

## Project Structure

```
flyde-mcp-project/
├── examples/                    # Interactive examples
│   ├── hello-world/            # Basic Flyde introduction
│   ├── ai-agent/               # AI agent workflow
│   ├── data-pipeline/          # ETL data processing
│   ├── mcp-integration/        # MCP tools integration
│   └── playground.js           # Interactive playground
├── src/                        # Source code
│   └── index.ts               # Main entry point
├── docs/                       # Documentation
│   └── flyde-complete-guide.md # Comprehensive guide
├── package.json               # Dependencies
├── tsconfig.json             # TypeScript config
└── README.md                 # Project overview
```

## Examples Overview

### 1. Hello World (`examples/hello-world/`)
- **Purpose**: Basic Flyde introduction
- **Features**: Simple data flow, input/output handling
- **Files**: `hello-world.flyde`, `index.ts`
- **Run**: `node examples/hello-world/index.ts`

### 2. AI Agent (`examples/ai-agent/`)
- **Purpose**: Complete AI agent implementation
- **Features**: Input processing, AI analysis, response generation
- **Files**: `ai-agent.flyde`, `index.ts`
- **Run**: `node examples/ai-agent/index.ts`

### 3. Data Pipeline (`examples/data-pipeline/`)
- **Purpose**: ETL data processing pipeline
- **Features**: Data validation, transformation, aggregation
- **Files**: `data-pipeline.flyde`, `index.ts`
- **Run**: `node examples/data-pipeline/index.ts`

### 4. MCP Integration (`examples/mcp-integration/`)
- **Purpose**: MCP tools integration with Flyde
- **Features**: Web crawling, browser automation, file operations
- **Files**: `mcp-integration.flyde`, `mcp-flyde-bridge.ts`, `index.ts`
- **Run**: `node examples/mcp-integration/index.ts`

## Development

### Creating New Flows

1. **Using VSCode Extension**:
   - Open VSCode
   - Command Palette (Ctrl+Shift+P)
   - Type "Flyde: New visual flow"
   - Design your flow visually

2. **Manual Creation**:
   - Create `.flyde` file with JSON structure
   - Define nodes and connections
   - Integrate with TypeScript code

### Custom Nodes

Create reusable components in TypeScript:

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

## Troubleshooting

### Common Issues

1. **Module not found errors**:
   ```bash
   npm install @flyde/loader @flyde/nodes @flyde/core
   ```

2. **Flow execution errors**:
   - Check node connections
   - Verify input/output types
   - Check console for error messages

3. **TypeScript compilation errors**:
   ```bash
   npm run build
   ```

### Getting Help

- [Flyde Documentation](https://flyde.dev/docs)
- [GitHub Issues](https://github.com/flydelabs/flyde/issues)
- [Discord Community](https://www.flyde.dev/discord)

## Next Steps

1. **Explore Examples**: Run each example to understand Flyde concepts
2. **Modify Flows**: Try changing the visual flows in the editor
3. **Create Custom Nodes**: Build reusable components for your needs
4. **Integrate MCP**: Use MCP tools for enhanced functionality
5. **Build Your Own**: Create flows for your specific use cases

## Resources

- [Flyde Official Site](https://flyde.dev)
- [Online Playground](https://flyde.dev/playground)
- [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=flyde.flyde-vscode)
- [GitHub Repository](https://github.com/flydelabs/flyde)

---

**Happy visual programming! 🚀**