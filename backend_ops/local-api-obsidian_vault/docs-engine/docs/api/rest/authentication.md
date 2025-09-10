# Authentication

The Obsidian Vault AI System uses JWT-based authentication for secure API access.

## Authentication Methods

### JWT Token Authentication

All API endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### API Key Authentication

For some endpoints, you can use an API key:

```http
X-API-Key: <your-api-key>
```

## Getting Started

1. **Register a new user** via the `/auth/register` endpoint
2. **Login** via the `/auth/login` endpoint to get your JWT token
3. **Include the token** in all subsequent API requests

## Example

```bash
curl -X POST "http://localhost:8085/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

## Token Refresh

JWT tokens expire after 24 hours. Use the refresh endpoint to get a new token:

```bash
curl -X POST "http://localhost:8085/auth/refresh" \
  -H "Authorization: Bearer <your-current-token>"
```

## Security Notes

- Always use HTTPS in production
- Store tokens securely
- Never expose tokens in client-side code
- Implement proper token rotation
