# Enhanced Mermaid Diagrams

This page showcases high-contrast, dark-themed Mermaid diagrams with enhanced visual rendering.

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Obsidian Client] --> B[Web Interface]
        B --> C[Mobile API]
    end
    
    subgraph "API Gateway Layer"
        D[Nginx Reverse Proxy] --> E[Load Balancer]
        E --> F[Rate Limiter]
    end
    
    subgraph "Application Layer"
        G[FastAPI Backend] --> H[n8n Workflows]
        H --> I[AI Agents]
        I --> J[MCP Tools]
    end
    
    subgraph "Data Layer"
        K[PostgreSQL] --> L[Redis Cache]
        L --> M[ChromaDB Vector]
        M --> N[File System]
    end
    
    subgraph "Infrastructure Layer"
        O[Docker Containers] --> P[Monitoring]
        P --> Q[Logging]
        Q --> R[Security]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant V as Vault API
    participant O as Obsidian API
    participant A as AI Service
    participant D as Database
    
    U->>V: Create file request
    V->>O: Validate vault access
    O->>V: Access confirmed
    V->>A: Generate content
    A->>V: Generated content
    V->>O: Write file to vault
    O->>V: File created
    V->>D: Store metadata
    V->>U: Success response
```

## Workflow Timeline

```mermaid
gantt
    title AI Workflow Processing
    dateFormat  YYYY-MM-DD
    section Data Collection
    Vault Scanning    :active, vault, 2024-01-01, 2d
    Content Analysis  :analysis, after vault, 1d
    section AI Processing
    RAG Generation    :rag, after analysis, 2d
    Agent Execution   :agent, after rag, 1d
    section Output
    Result Storage    :storage, after agent, 1d
    User Notification :notify, after storage, 1d
```

## Visual Components

### Enhanced Cards
<div class="visual-card">
  <h3>System Status</h3>
  <p>All services are running optimally with enhanced monitoring.</p>
  <div class="visual-status success">✓ Healthy</div>
</div>

### Enhanced Buttons
<button class="visual-button">Enhanced Action</button>

### Enhanced Code Blocks
<div class="visual-code">
```python
def enhanced_function():
    return "High contrast visual rendering"
```
</div>

### Enhanced Tables
<table class="visual-table">
  <thead>
    <tr>
      <th>Service</th>
      <th>Status</th>
      <th>Performance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Vault API</td>
      <td><div class="visual-status success">✓ Running</div></td>
      <td><div class="visual-progress"><div class="visual-progress-bar" style="width: 95%"></div></div></td>
    </tr>
    <tr>
      <td>Obsidian API</td>
      <td><div class="visual-status success">✓ Running</div></td>
      <td><div class="visual-progress"><div class="visual-progress-bar" style="width: 88%"></div></div></td>
    </tr>
    <tr>
      <td>n8n Workflows</td>
      <td><div class="visual-status warning">⚠ Processing</div></td>
      <td><div class="visual-progress"><div class="visual-progress-bar" style="width: 72%"></div></div></td>
    </tr>
  </tbody>
</table>
