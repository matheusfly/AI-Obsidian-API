# Real-time WebSocket API

The Obsidian Vault AI System provides real-time communication through WebSocket connections.

## Connection

Connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8085/ws');
```

## Authentication

Include your JWT token in the connection URL:

```javascript
const ws = new WebSocket('ws://localhost:8085/ws?token=<your-jwt-token>');
```

## Message Format

All messages are JSON formatted:

```json
{
  "type": "message_type",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Message Types

### Vault Updates
```json
{
  "type": "vault_update",
  "data": {
    "file_path": "/path/to/file.md",
    "action": "created|updated|deleted",
    "content": "file content"
  }
}
```

### AI Processing Status
```json
{
  "type": "ai_status",
  "data": {
    "task_id": "uuid",
    "status": "processing|completed|failed",
    "progress": 50
  }
}
```

### System Notifications
```json
{
  "type": "notification",
  "data": {
    "level": "info|warning|error",
    "message": "System message",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Error Handling

```json
{
  "type": "error",
  "data": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid token",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Example Usage

```javascript
const ws = new WebSocket('ws://localhost:8085/ws?token=your-token');

ws.onopen = function(event) {
  console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'vault_update':
      handleVaultUpdate(message.data);
      break;
    case 'ai_status':
      handleAIStatus(message.data);
      break;
    case 'notification':
      handleNotification(message.data);
      break;
    case 'error':
      handleError(message.data);
      break;
  }
};

ws.onclose = function(event) {
  console.log('WebSocket connection closed');
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};
```
