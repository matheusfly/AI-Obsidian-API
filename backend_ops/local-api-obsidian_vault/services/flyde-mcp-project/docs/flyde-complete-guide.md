# 🚀 Complete Flyde Guide - Visual Programming for AI Agents

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Getting Started](#getting-started)
4. [Built-in Nodes](#built-in-nodes)
5. [Integration Patterns](#integration-patterns)
6. [Advanced Examples](#advanced-examples)
7. [MCP Integration](#mcp-integration)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

Flyde is a visual, flow-based programming toolkit that **integrates with your existing code**. It's particularly powerful for building AI agent workflows, data pipelines, and complex business logic that benefits from visual representation.

### Why Flyde for AI Agents?

- **Visual Clarity**: See your agent's logic flow at a glance
- **Easy Debugging**: Visual execution makes issues obvious
- **Team Collaboration**: Non-technical team members can understand flows
- **Rapid Iteration**: Modify flows without deep code changes
- **Integration**: Works seamlessly with existing TypeScript code

## Core Concepts

### 1. Nodes
Each node in Flyde is an isolated, modular unit that runs some logic when executed. A node has:
- **Inputs**: Data that flows into the node
- **Outputs**: Data that flows out of the node
- **Logic**: The processing that happens inside

### 2. Connections
Nodes are connected together using connections (wires) that allow them to communicate. Each connection connects an output of one node to an input of another node.

### 3. Flows
A Flyde flow consists of nodes and connections between them. Flows can also have:
- **Main Inputs**: Entry points for external data
- **Main Outputs**: Exit points for processed data

### 4. Custom Nodes
You can create reusable components for specific functionality using TypeScript/JavaScript.

## Getting Started

### Installation

```bash
# Install Flyde packages
npm install @flyde/loader @flyde/nodes @flyde/core

# Install VSCode extension
# Search for "Flyde" in VSCode extensions
```

### Basic Example

```typescript
import { runFlow } from '@flyde/loader';

// Execute a flow
const result = await runFlow('./my-flow.flyde', {
  input1: 'Hello',
  input2: 'World'
});

console.log(result.output1); // Processed result
```

### Creating Your First Flow

1. Open VSCode
2. Command Palette (Ctrl+Shift+P) → `Flyde: New visual flow`
3. Design your flow visually
4. Integrate with TypeScript code

## Built-in Nodes

### Control Flow
- **Conditional**: Branch based on conditions
- **Switch**: Multi-way branching
- **Loop List**: Iterate over arrays

### Value Nodes
- **Value**: Constant values
- **Variable**: Mutable state
- **Math**: Mathematical operations

### Data Processing
- **Array**: Array operations
- **Object**: Object manipulation
- **String**: String processing
- **JSON**: JSON parsing/stringifying

### I/O Nodes
- **Console**: Log to console
- **HTTP**: Make HTTP requests
- **File**: File operations

## Integration Patterns

### 1. Simple Integration

```typescript
import { runFlow } from '@flyde/loader';

const result = await runFlow('./simple-flow.flyde', {
  input: 'Hello World'
});
```

### 2. Advanced Integration

```typescript
import { loadFlow } from '@flyde/loader';

const execute = await loadFlow('./complex-flow.flyde');

const { result } = execute(inputs, {
  onOutputs: (key, value) => {
    console.log(`Output ${key}: ${value}`);
  }
});
```

### 3. Custom Nodes

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

## Advanced Examples

### 1. AI Agent Workflow

```yaml
# ai-agent.flyde
nodes:
  - id: input-processor
    type: Code
    code: |
      const processed = {
        original: inputs.message,
        timestamp: new Date().toISOString(),
        length: inputs.message.length
      };
      outputs.processed.next(processed);
  
  - id: ai-analyzer
    type: Code
    code: |
      const analysis = {
        sentiment: 'positive',
        confidence: 0.85,
        topics: ['ai', 'programming']
      };
      outputs.analysis.next(analysis);
  
  - id: response-generator
    type: Code
    code: |
      const response = {
        message: `I analyzed: "${inputs.data.original}"`,
        insights: inputs.analysis,
        timestamp: new Date().toISOString()
      };
      outputs.response.next(response);
```

### 2. Data Pipeline

```yaml
# data-pipeline.flyde
nodes:
  - id: data-source
    type: Code
    code: |
      const data = [
        { id: 1, name: 'John', age: 30 },
        { id: 2, name: 'Jane', age: 25 }
      ];
      outputs.data.next(data);
  
  - id: validator
    type: Code
    code: |
      const valid = inputs.data.filter(record => 
        record.id && record.name && record.age > 0
      );
      outputs.valid.next(valid);
  
  - id: transformer
    type: Code
    code: |
      const transformed = inputs.data.map(record => ({
        ...record,
        name: record.name.toUpperCase(),
        ageGroup: record.age < 30 ? 'young' : 'adult'
      }));
      outputs.transformed.next(transformed);
```

## MCP Integration

### Web Crawling with MCP

```typescript
// Use MCP tools to fetch documentation
import { mcp_fetch_content } from '@mcp/tools';

const docs = await mcp_fetch_content('https://flyde.dev/docs');
console.log('Documentation fetched:', docs);
```

### Real-time Monitoring

```typescript
// Monitor flow execution with MCP
import { mcp_playwright_browser_snapshot } from '@mcp/tools';

const snapshot = await mcp_playwright_browser_snapshot();
console.log('Current state:', snapshot);
```

## Best Practices

### 1. Flow Design
- Keep flows focused and single-purpose
- Use descriptive node names
- Add comments to complex logic
- Test flows with various inputs

### 2. Error Handling
- Always validate inputs
- Handle edge cases gracefully
- Log errors for debugging
- Provide meaningful error messages

### 3. Performance
- Avoid blocking operations in nodes
- Use streaming for large datasets
- Cache expensive computations
- Monitor execution times

### 4. Collaboration
- Document your flows
- Use version control
- Share reusable components
- Code review flows

## Troubleshooting

### Common Issues

1. **Flow not executing**
   - Check input/output connections
   - Verify node configurations
   - Check console for errors

2. **Data not flowing**
   - Ensure proper connections
   - Check data types match
   - Verify node logic

3. **Performance issues**
   - Profile execution times
   - Optimize node logic
   - Consider parallel processing

### Debugging Tips

1. Use console.log in nodes
2. Check the visual flow editor
3. Test with simple inputs first
4. Use the playground for experimentation

## Resources

- [Official Documentation](https://flyde.dev/docs)
- [GitHub Repository](https://github.com/flydelabs/flyde)
- [Online Playground](https://flyde.dev/playground)
- [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=flyde.flyde-vscode)
- [Discord Community](https://www.flyde.dev/discord)

## Conclusion

Flyde provides a powerful way to build visual workflows that integrate seamlessly with your existing codebase. Whether you're building AI agents, data pipelines, or complex business logic, Flyde's visual approach makes your code more maintainable, debuggable, and collaborative.

The combination of Flyde's visual programming with MCP tools creates a powerful environment for building sophisticated AI agent workflows that are both powerful and easy to understand.

---

*Happy visual programming! 🚀*