# Your First Workflow

Create your first automated workflow with the Obsidian Vault AI System.

## Prerequisites

- System running (see [Quick Start Guide](/docs/getting-started/quick-start))
- n8n accessible at [http://localhost:5678](http://localhost:5678)
- Basic understanding of workflows

## Workflow 1: Daily Note Generator

Create an automated workflow that generates a daily note with AI-powered content.

### Step 1: Access n8n

1. Open [http://localhost:5678](http://localhost:5678)
2. Login with your credentials
3. Click "Create Workflow"

### Step 2: Set Up the Workflow

#### Node 1: Schedule Trigger

1. Add a **Schedule Trigger** node
2. Configure:
   - **Trigger Interval**: `0 9 * * *` (9 AM daily)
   - **Timezone**: Your timezone

#### Node 2: Get Current Date

1. Add a **Set** node
2. Configure:
   - **Keep Only Set Fields**: `true`
   - **Fields to Set**:
     - `date`: `{{ new Date().toISOString().split('T')[0] }}`
     - `formatted_date`: `{{ new Date().toLocaleDateString() }}`

#### Node 3: Generate AI Content

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/ai/generate`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "prompt": "Generate a daily note template for {{ $json.formatted_date }}. Include sections for: 1) Today's goals, 2) Important tasks, 3) Notes and ideas, 4) Reflection questions. Make it inspiring and actionable.",
       "max_tokens": 1000
     }
     ```

#### Node 4: Create File

1. Add another **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/vault/files`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "path": "Daily Notes/{{ $json.date }}.md",
       "content": "# Daily Note - {{ $json.formatted_date }}\n\n{{ $json.content }}"
     }
     ```

#### Node 5: Send Notification

1. Add a **Slack** or **Email** node
2. Configure to send a notification when the daily note is created

### Step 3: Test the Workflow

1. Click "Execute Workflow" to test
2. Check the execution log for any errors
3. Verify the file was created in your vault

## Workflow 2: Content Summarizer

Create a workflow that automatically summarizes new files in your vault.

### Step 1: File Watcher

1. Add a **Webhook** node
2. Configure:
   - **HTTP Method**: `POST`
   - **Path**: `file-created`

### Step 2: Process File

1. Add a **Function** node
2. Configure:
   ```javascript
   // Extract file information
   const filePath = $input.first().json.path;
   const fileName = filePath.split('/').pop();
   
   return {
     file_path: filePath,
     file_name: fileName,
     timestamp: new Date().toISOString()
   };
   ```

### Step 3: Generate Summary

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/ai/generate`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "prompt": "Summarize the following content in 3-5 bullet points, highlighting key insights and actionable items:",
       "context_files": ["{{ $json.file_path }}"],
       "max_tokens": 500
     }
     ```

### Step 4: Create Summary File

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/vault/files`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "path": "Summaries/{{ $json.file_name }}.summary.md",
       "content": "# Summary of {{ $json.file_name }}\n\n{{ $json.content }}\n\n---\n*Generated on {{ $json.timestamp }}*"
     }
     ```

## Workflow 3: Knowledge Graph Builder

Create a workflow that builds a knowledge graph from your vault content.

### Step 1: Weekly Trigger

1. Add a **Schedule Trigger** node
2. Configure:
   - **Trigger Interval**: `0 0 * * 0` (Weekly on Sunday)
   - **Timezone**: Your timezone

### Step 2: Get All Files

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `GET`
   - **URL**: `http://vault-api:8080/vault/files`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`

### Step 3: Process Files

1. Add a **Function** node
2. Configure:
   ```javascript
   // Process each file
   const files = $input.first().json.files;
   const processedFiles = files.map(file => ({
     path: file.path,
     name: file.path.split('/').pop(),
     size: file.size,
     modified: file.modified
   }));
   
   return processedFiles.map(file => ({ json: file }));
   ```

### Step 4: Extract Entities

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/ai/analyze`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "file_path": "{{ $json.path }}",
       "analysis_type": "entity_extraction",
       "entities": ["PERSON", "ORG", "GPE", "EVENT", "CONCEPT"]
     }
     ```

### Step 5: Build Graph

1. Add a **Function** node
2. Configure:
   ```javascript
   // Build knowledge graph
   const entities = $input.first().json.entities;
   const filePath = $input.first().json.file_path;
   
   // Create graph nodes and edges
   const nodes = entities.map(entity => ({
     id: entity.text,
     label: entity.text,
     type: entity.label,
     file: filePath
   }));
   
   const edges = entities.map(entity => ({
     source: filePath,
     target: entity.text,
     relationship: "contains"
   }));
   
   return {
     nodes: nodes,
     edges: edges,
     file: filePath
   };
   ```

### Step 6: Save Graph

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/vault/files`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "path": "Knowledge Graph/graph.json",
       "content": "{{ JSON.stringify($json) }}"
     }
     ```

## Workflow 4: MCP Tool Integration

Create a workflow that uses MCP tools for enhanced functionality.

### Step 1: GitHub Integration

1. Add a **Schedule Trigger** node
2. Configure:
   - **Trigger Interval**: `0 0 * * *` (Daily)

### Step 2: Get GitHub Issues

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/mcp/call`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "tool": "github",
       "operation": "list_issues",
       "parameters": {
         "owner": "your-username",
         "repo": "your-repo",
         "state": "open"
       }
     }
     ```

### Step 3: Process Issues

1. Add a **Function** node
2. Configure:
   ```javascript
   // Process GitHub issues
   const issues = $input.first().json.result;
   const processedIssues = issues.map(issue => ({
     title: issue.title,
     body: issue.body,
     url: issue.html_url,
     created_at: issue.created_at,
     updated_at: issue.updated_at,
     labels: issue.labels.map(label => label.name)
   }));
   
   return processedIssues.map(issue => ({ json: issue }));
   ```

### Step 4: Create Issue Notes

1. Add a **HTTP Request** node
2. Configure:
   - **Method**: `POST`
   - **URL**: `http://vault-api:8080/vault/files`
   - **Headers**:
     - `Authorization`: `Bearer your-jwt-token`
     - `Content-Type`: `application/json`
   - **Body**:
     ```json
     {
       "path": "GitHub Issues/{{ $json.title.replace(/[^a-zA-Z0-9]/g, '_') }}.md",
       "content": "# {{ $json.title }}\n\n**URL**: {{ $json.url }}\n**Created**: {{ $json.created_at }}\n**Updated**: {{ $json.updated_at }}\n\n**Labels**: {{ $json.labels.join(', ') }}\n\n## Description\n\n{{ $json.body }}"
     }
     ```

## Testing Your Workflows

### Manual Testing

1. Click "Execute Workflow" in n8n
2. Check the execution log
3. Verify outputs in your vault

### Automated Testing

```python
# test_workflow.py
import requests
import json

def test_daily_note_workflow():
    """Test the daily note workflow."""
    # Trigger the workflow
    response = requests.post(
        "http://localhost:5678/webhook/daily-note",
        json={"test": True}
    )
    
    assert response.status_code == 200
    
    # Check if file was created
    files_response = requests.get(
        "http://localhost:8085/vault/files",
        headers={"Authorization": "Bearer your-token"}
    )
    
    files = files_response.json()
    today = datetime.now().strftime("%Y-%m-%d")
    
    assert any(f"Daily Notes/{today}.md" in file["path"] for file in files["files"])

if __name__ == "__main__":
    test_daily_note_workflow()
    print("All tests passed!")
```

## Best Practices

1. **Start Simple**: Begin with basic workflows and add complexity gradually
2. **Test Thoroughly**: Always test workflows before enabling them
3. **Handle Errors**: Add error handling nodes to your workflows
4. **Use Variables**: Store configuration in n8n variables
5. **Document Workflows**: Add descriptions to your workflow nodes
6. **Monitor Performance**: Check execution times and resource usage
7. **Backup Workflows**: Export your workflows regularly

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check your JWT token and API keys
2. **File Path Issues**: Ensure vault paths are correct
3. **Rate Limiting**: Add delays between API calls if needed
4. **Memory Issues**: Process files in batches for large operations

### Debug Tips

1. Use the **Function** node to log data
2. Check the execution log for detailed error messages
3. Test individual nodes before connecting them
4. Use the **Set** node to modify data between nodes

## Next Steps

1. **Explore More Workflows**: Check out the [Workflow Gallery](../guides/workflows)
2. **Learn Advanced Features**: Read about [Advanced Workflows](../advanced/workflows)
3. **Share Your Workflows**: Contribute to the community
4. **Monitor Performance**: Set up [Monitoring](../deployment/monitoring)

Happy workflow building! 🚀
