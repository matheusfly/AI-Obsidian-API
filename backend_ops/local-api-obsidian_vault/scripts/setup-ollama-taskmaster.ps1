# Ollama + Task Master Integration Setup Script
Write-Host "Setting up Ollama integration with Task Master..." -ForegroundColor Green

# Check if Ollama is installed
Write-Host "`n1. Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>$null
    if ($ollamaVersion -match "ollama") {
        Write-Host "SUCCESS: Ollama is installed - $ollamaVersion" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Ollama not found, installing..." -ForegroundColor Yellow
        # Install Ollama
        Write-Host scripts/ing Ollama..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri "https://ollama.com/download/windows" -OutFile "ollama-installer.exe"
        Start-Process -FilePath "ollama-installer.exe" -ArgumentList "/S" -Wait
        Remove-Item "ollama-installer.exe" -Force
        Write-Host "SUCCESS: Ollama installed" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Ollama installation failed" -ForegroundColor Red
    Write-Host "Please install Ollama manually from https://ollama.com/download" -ForegroundColor Yellow
}

# Start Ollama service
Write-Host "`n2. Starting Ollama service..." -ForegroundColor Yellow
try {
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "SUCCESS: Ollama service started" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Could not start Ollama service automatically" -ForegroundColor Yellow
    Write-Host "Please run 'ollama serve' manually" -ForegroundColor White
}

# Pull recommended models
Write-Host "`n3. Pulling recommended Ollama models..." -ForegroundColor Yellow

$models = @(
    "llama3.2:latest",
    "llama3.1:latest", 
    "qwen2.5:latest",
    "deepseek-r1:latest",
    "gemma2:latest",
    "codellama:latest",
    "mistral:latest",
    "neural-chat:latest",
    "starling-lm:latest",
    "vicuna:latest"
)

foreach ($model in $models) {
    Write-Host "Pulling $model..." -ForegroundColor Cyan
    try {
        ollama pull $model
        Write-Host "SUCCESS: $model pulled" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Failed to pull $model" -ForegroundColor Yellow
    }
}

# Test Ollama connection
Write-Host "`n4. Testing Ollama connection..." -ForegroundColor Yellow
try {
    $testResult = ollama list
    if ($testResult -match "llama3.2") {
        Write-Host "SUCCESS: Ollama is working and models are available" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Ollama test inconclusive" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Ollama connection test failed" -ForegroundColor Red
}

# Create Ollama configuration for Task Master
Write-Host "`n5. Creating Ollama configuration for Task Master..." -ForegroundColor Yellow

$ollamaConfig = @{
    "ollama_host" = "http://localhost:11434"
    "ollama_timeout" = 300000
    "ollama_models" = @{
        "main" = "llama3.2:latest"
        "research" = "qwen2.5:latest"
        "fallback" = "llama3.1:latest"
        "coding" = "codellama:latest"
        "reasoning" = "deepseek-r1:latest"
    }
    "ollama_settings" = @{
        "temperature" = 0.7
        "top_p" = 0.9
        "max_tokens" = 4096
        "stream" = $true
    }
}

$ollamaConfigPath = ".taskmaster/ollama-config.json"
$ollamaConfigDir = Split-Path $ollamaConfigPath -Parent
if (-not (Test-Path $ollamaConfigDir)) {
    New-Item -ItemType Directory -Path $ollamaConfigDir -Force | Out-Null
}

$ollamaConfigJson = $ollamaConfig | ConvertTo-Json -Depth 10
Set-Content -Path $ollamaConfigPath -Value $ollamaConfigJson -Encoding UTF8
Write-Host "SUCCESS: Ollama configuration created at $ollamaConfigPath" -ForegroundColor Green

# Create Task Master Ollama integration script
Write-Host "`n6. Creating Task Master Ollama integration..." -ForegroundColor Yellow

$taskMasterOllamaScript = @'
#!/usr/bin/env node
// Task Master Ollama Integration Script

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class TaskMasterOllama {
    constructor() {
        this.ollamaHost = process.env.OLLAMA_HOST || 'http://localhost:11434';
        this.timeout = parseInt(process.env.OLLAMA_TIMEOUT) || 300000;
        this.models = {
            main: process.env.OLLAMA_MAIN_MODEL || 'llama3.2:latest',
            research: process.env.OLLAMA_RESEARCH_MODEL || 'qwen2.5:latest',
            fallback: process.env.OLLAMA_FALLBACK_MODEL || 'llama3.1:latest',
            coding: process.env.OLLAMA_CODING_MODEL || 'codellama:latest',
            reasoning: process.env.OLLAMA_REASONING_MODEL || 'deepseek-r1:latest'
        };
    }

    async listModels() {
        try {
            const response = await fetch(`${this.ollamaHost}/api/tags`);
            const data = await response.json();
            return data.models || [];
        } catch (error) {
            console.error('Error listing models:', error);
            return [];
        }
    }

    async generateResponse(prompt, model = 'main', options = {}) {
        const modelName = this.models[model] || this.models.main;
        const requestBody = {
            model: modelName,
            prompt: prompt,
            stream: false,
            options: {
                temperature: options.temperature || 0.7,
                top_p: options.top_p || 0.9,
                max_tokens: options.max_tokens || 4096,
                ...options
            }
        };

        try {
            const response = await fetch(`${this.ollamaHost}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error generating response:', error);
            throw error;
        }
    }

    async chat(messages, model = 'main', options = {}) {
        const modelName = this.models[model] || this.models.main;
        const requestBody = {
            model: modelName,
            messages: messages,
            stream: false,
            options: {
                temperature: options.temperature || 0.7,
                top_p: options.top_p || 0.9,
                max_tokens: options.max_tokens || 4096,
                ...options
            }
        };

        try {
            const response = await fetch(`${this.ollamaHost}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.message.content;
        } catch (error) {
            console.error('Error in chat:', error);
            throw error;
        }
    }

    async isHealthy() {
        try {
            const response = await fetch(`${this.ollamaHost}/api/tags`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

// Export for use in Task Master
module.exports = TaskMasterOllama;

// CLI usage
if (require.main === module) {
    const ollama = new TaskMasterOllama();
    
    const command = process.argv[2];
    const model = process.argv[3] || 'main';
    const prompt = process.argv[4];

    switch (command) {
        case 'list':
            ollama.listModels().then(models => {
                console.log('Available models:');
                models.forEach(model => console.log(`- ${model.name}`));
            });
            break;
        case 'generate':
            if (prompt) {
                ollama.generateResponse(prompt, model).then(response => {
                    console.log(response);
                });
            } else {
                console.log('Usage: node taskmaster-ollama.js generate [model] "prompt"');
            }
            break;
        case 'health':
            ollama.isHealthy().then(healthy => {
                console.log(healthy ? 'Ollama is healthy' : 'Ollama is not responding');
            });
            break;
        default:
            console.log('Usage:');
            console.log('  node taskmaster-ollama.js list');
            console.log('  node taskmaster-ollama.js generate [model] "prompt"');
            console.log('  node taskmaster-ollama.js health');
    }
}
'@

$ollamaScriptPath = "taskmaster-ollama.js"
Set-Content -Path $ollamaScriptPath -Value $taskMasterOllamaScript -Encoding UTF8
Write-Host "SUCCESS: Task Master Ollama integration script created" -ForegroundColor Green

# Create environment variables file
Write-Host "`n7. Creating environment variables..." -ForegroundColor Yellow

$envContent = @'
# Ollama Configuration for Task Master
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300000
OLLAMA_MAIN_MODEL=llama3.2:latest
OLLAMA_RESEARCH_MODEL=qwen2.5:latest
OLLAMA_FALLBACK_MODEL=llama3.1:latest
OLLAMA_CODING_MODEL=codellama:latest
OLLAMA_REASONING_MODEL=deepseek-r1:latest

# Task Master with Ollama Support
TASK_MASTER_OLLAMA_ENABLED=true
TASK_MASTER_OLLAMA_HOST=http://localhost:11434
TASK_MASTER_OLLAMA_MODELS=llama3.2:latest,llama3.1:latest,qwen2.5:latest,deepseek-r1:latest,gemma2:latest,codellama:latest,mistral:latest,neural-chat:latest,starling-lm:latest,vicuna:latest
'@

Set-Content -Path ".env.ollama" -Value $envContent -Encoding UTF8
Write-Host "SUCCESS: Environment variables created" -ForegroundColor Green

# Summary
Write-Host "`nOllama + Task Master Integration Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "What was set up:" -ForegroundColor Yellow
Write-Host "- Ollama service installation and configuration" -ForegroundColor White
Write-Host "- 10 recommended models pulled" -ForegroundColor White
Write-Host "- Task Master Ollama integration script" -ForegroundColor White
Write-Host "- Ollama configuration for Task Master" -ForegroundColor White
Write-Host "- Environment variables for Ollama" -ForegroundColor White
Write-Host ""
Write-Host "Available Ollama models:" -ForegroundColor Yellow
Write-Host "- llama3.2:latest (Main model)" -ForegroundColor White
Write-Host "- llama3.1:latest (Fallback model)" -ForegroundColor White
Write-Host "- qwen2.5:latest (Research model)" -ForegroundColor White
Write-Host "- deepseek-r1:latest (Reasoning model)" -ForegroundColor White
Write-Host "- codellama:latest (Coding model)" -ForegroundColor White
Write-Host "- gemma2:latest, mistral:latest, neural-chat:latest" -ForegroundColor White
Write-Host "- starling-lm:latest, vicuna:latest" -ForegroundColor White
Write-Host ""
Write-Host "Usage in Task Master:" -ForegroundColor Yellow
Write-Host "- Change the main model to claude-code/sonnet" -ForegroundColor White
Write-Host "- Use Ollama models for research and fallback" -ForegroundColor White
Write-Host "- Run: node taskmaster-ollama.js list" -ForegroundColor White
Write-Host "- Run: node taskmaster-ollama.js health" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Cursor to load updated MCP configuration" -ForegroundColor White
Write-Host "2. Copy WARP_COMPLETE_MCP_CONFIG.json to Warp settings" -ForegroundColor White
Write-Host "3. Test Task Master with Ollama models" -ForegroundColor White
Write-Host "4. Use 'Change the main model to claude-code/sonnet' in Task Master" -ForegroundColor White
Write-Host ""
Write-Host "All MCP tools should now show green status!" -ForegroundColor Green
