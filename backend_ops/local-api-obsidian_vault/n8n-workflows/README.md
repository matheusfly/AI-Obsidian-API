# 🤖 Obsidian Vault Q&A Chatbot - n8n Workflows

This directory contains n8n workflows for creating an intelligent Q&A chatbot that can answer questions about your Obsidian vault content.

## 📋 **Available Workflows**

### 1. **Complete Q&A Chatbot** (`obsidian-qa-chatbot.json`)
A full-featured workflow with AI-powered responses using Ollama.

**Features:**
- ✅ Webhook trigger for questions
- ✅ Vault content search
- ✅ AI-powered answer generation (Ollama)
- ✅ Context-aware responses
- ✅ Source attribution
- ✅ Special commands (vault stats, recent files)
- ✅ Error handling

### 2. **Simple Search** (`obsidian-qa-simple.json`)
A lightweight workflow for basic vault search functionality.

**Features:**
- ✅ Webhook trigger
- ✅ Basic vault search
- ✅ JSON response
- ✅ Minimal dependencies

## 🚀 **Quick Start**

### **Step 1: Import Workflow to n8n**

1. **Access n8n Interface:**
   ```bash
   # Start n8n (if not already running)
   docker-compose up n8n -d
   
   # Access n8n at: http://localhost:5678
   ```

2. **Import Workflow:**
   - Open n8n interface
   - Click "Import from File"
   - Select `obsidian-qa-simple.json` (start with simple version)
   - Click "Import"

3. **Activate Workflow:**
   - Click the "Active" toggle in the top right
   - The workflow is now ready to receive requests

### **Step 2: Test the Workflow**

**Test with curl:**
```bash
# Test simple search
curl -X POST http://localhost:5678/webhook/obsidian-simple \
  -H "Content-Type: application/json" \
  -d '{"question": "What files contain AI or agent information?"}'

# Test with different query
curl -X POST http://localhost:5678/webhook/obsidian-simple \
  -H "Content-Type: application/json" \
  -d '{"query": "context engineering"}'
```

**Test with PowerShell:**
```powershell
# Test the workflow
$body = @{
    question = "What files contain AI or agent information?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/obsidian-simple" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

## 🔧 **Workflow Configuration**

### **Environment Variables Required:**

```bash
# In your .env file
VAULT_PATH=D:\Nomade Milionario
API_KEY=obsidian_secure_key_2024
OLLAMA_HOST=http://ollama:11434
N8N_WEBHOOK_URL=http://localhost:5678
```

### **Service Dependencies:**

1. **vault-api** (port 8080) - Must be running
2. **n8n** (port 5678) - Must be running
3. **ollama** (port 11434) - Required for AI features (complete workflow only)

## 📊 **API Endpoints**

### **Simple Workflow:**
- **URL:** `http://localhost:5678/webhook/obsidian-simple`
- **Method:** POST
- **Body:** `{"question": "your question here"}`

### **Complete Workflow:**
- **URL:** `http://localhost:5678/webhook/obsidian-qa`
- **Method:** POST
- **Body:** `{"question": "your question here"}`

## 🎯 **Usage Examples**

### **1. Basic Questions:**
```json
{
  "question": "What files contain information about AI agents?"
}
```

### **2. Vault Statistics:**
```json
{
  "question": "vault stats"
}
```

### **3. Recent Files:**
```json
{
  "question": "recent files"
}
```

### **4. Content Search:**
```json
{
  "question": "context engineering implementation"
}
```

## 🔍 **Response Format**

### **Simple Workflow Response:**
```json
{
  "status": "success",
  "question": "What files contain AI information?",
  "results": [
    {
      "title": "AGENTS.md",
      "path": "AGENTS.md",
      "content": "AI agents implementation...",
      "relevance_score": 0.95
    }
  ],
  "message": "Search completed successfully"
}
```

### **Complete Workflow Response:**
```json
{
  "status": "success",
  "question": "What files contain AI information?",
  "answer": "Based on your vault content, I found several files related to AI agents...",
  "sources": [
    {
      "title": "AGENTS.md",
      "path": "AGENTS.md",
      "relevance": 0.95
    }
  ],
  "metadata": {
    "sources_count": 3,
    "timestamp": "2024-01-15T10:00:00.000Z",
    "model": "llama3.1:8b"
  }
}
```

## 🛠 **Troubleshooting**

### **Common Issues:**

1. **Workflow not triggering:**
   - Check if n8n is running: `docker-compose ps`
   - Verify webhook URL is correct
   - Check n8n logs: `docker-compose logs n8n`

2. **Vault API connection failed:**
   - Ensure vault-api is running: `docker-compose ps vault-api`
   - Check API key in workflow configuration
   - Verify vault-api health: `curl http://localhost:8080/health`

3. **Ollama connection failed (complete workflow):**
   - Ensure Ollama is running: `docker-compose ps ollama`
   - Check Ollama model is available: `docker exec -it ollama ollama list`
   - Install required model: `docker exec -it ollama ollama pull llama3.1:8b`

### **Debug Steps:**

1. **Check service status:**
   ```bash
   docker-compose ps
   ```

2. **View n8n execution logs:**
   - Go to n8n interface
   - Click on workflow executions
   - View detailed logs for each node

3. **Test individual services:**
   ```bash
   # Test vault-api
   curl http://localhost:8080/health
   
   # Test Ollama
   curl http://localhost:11434/api/tags
   ```

## 🔄 **Workflow Customization**

### **Adding New Features:**

1. **New Search Types:**
   - Add new HTTP Request nodes
   - Configure different vault-api endpoints
   - Add conditional logic for different query types

2. **Enhanced AI Responses:**
   - Modify the AI prompt in "Prepare Context" node
   - Add different models for different types of questions
   - Implement response caching

3. **Integration with Other Services:**
   - Add webhook triggers for other applications
   - Integrate with Slack, Discord, or other chat platforms
   - Add email notifications for important queries

## 📈 **Performance Optimization**

### **For Large Vaults:**

1. **Limit search results:**
   - Reduce `limit` parameter in search requests
   - Implement pagination for large result sets

2. **Cache frequent queries:**
   - Add Redis caching layer
   - Implement query result caching

3. **Optimize AI responses:**
   - Use smaller models for simple queries
   - Implement response streaming for long answers

## 🔐 **Security Considerations**

1. **API Key Protection:**
   - Use environment variables for API keys
   - Rotate keys regularly
   - Implement rate limiting

2. **Input Validation:**
   - Validate all user inputs
   - Sanitize search queries
   - Implement query length limits

3. **Access Control:**
   - Restrict webhook access
   - Implement authentication for sensitive operations
   - Log all queries for audit purposes

## 📚 **Additional Resources**

- [n8n Documentation](https://docs.n8n.io/)
- [Obsidian API Documentation](./API_ENDPOINTS_REFERENCE.md)
- [Vault API Reference](./COMPLETE_API_REFERENCE.md)
- [Docker Compose Guide](./docker-compose.yml)

## 🎉 **Success Metrics**

Track these metrics to measure workflow success:

- **Response Time:** < 5 seconds for simple queries
- **Accuracy:** > 80% relevant results
- **Uptime:** > 99% availability
- **User Satisfaction:** Positive feedback on answer quality

---

**Ready to start?** Import the simple workflow first, test it, then upgrade to the complete version for AI-powered responses!
