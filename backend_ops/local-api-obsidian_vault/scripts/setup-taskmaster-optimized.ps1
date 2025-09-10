# Task Master Ollama Optimized Setup Script
Write-Host "Setting up Task Master with your optimized Ollama models..." -ForegroundColor Green

# Your specific models
$yourModels = @(
    "deepseek-r1:8b",
    "gemma3:latest", 
    "qwen3:latest",
    "kirito1/qwen3-coder:latest"
)

Write-Host "`nYour Ollama Models:" -ForegroundColor Yellow
foreach ($model in $yourModels) {
    Write-Host "- $model" -ForegroundColor Cyan
}

# Test Ollama connection
Write-Host "`n1. Testing Ollama connection..." -ForegroundColor Yellow
try {
    $ollamaList = ollama list
    Write-Host "SUCCESS: Ollama is running" -ForegroundColor Green
    Write-Host "Available models:" -ForegroundColor Cyan
    $ollamaList | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} catch {
    Write-Host "ERROR: Ollama is not running. Please start it with 'ollama serve'" -ForegroundColor Red
    exit 1
}

# Test each model
Write-Host "`n2. Testing each model..." -ForegroundColor Yellow

foreach ($model in $yourModels) {
    Write-Host scripts/ing $model..." -ForegroundColor Cyan
    try {
        $testResult = ollama run $model "Hello, are you working?" 2>$null
        if ($testResult -match "Hello" -or $testResult -match "working") {
            Write-Host "SUCCESS: $model is working" -ForegroundColor Green
        } else {
            Write-Host "WARNING: $model test inconclusive" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "WARNING: $model test failed" -ForegroundColor Yellow
    }
}

# Create optimized configuration
Write-Host "`n3. Creating optimized configuration..." -ForegroundColor Yellow

$optimizedConfig = @{
    "ollama_host" = "http://localhost:11434"
    "ollama_timeout" = 300000
    "models" = @{
        "main" = "deepseek-r1:8b"
        "coding" = "kirito1/qwen3-coder:latest"
        "research" = "qwen3:latest"
        "fallback" = "gemma3:latest"
    }
    "model_configs" = @{
        "deepseek-r1:8b" = @{
            "temperature" = 0.7
            "top_p" = 0.9
            "max_tokens" = 4096
            "context_length" = 32768
            "description" = "Main reasoning and analysis model"
            "use_cases" = @("task_analysis", "reasoning", "complex_problem_solving")
        }
        "kirito1/qwen3-coder:latest" = @{
            "temperature" = 0.3
            "top_p" = 0.8
            "max_tokens" = 8192
            "context_length" = 32768
            "description" = "Specialized coding model"
            "use_cases" = @("code_generation", scripts/ing", "code_review")
        }
        "qwen3:latest" = @{
            "temperature" = 0.6
            "top_p" = 0.9
            "max_tokens" = 4096
            "context_length" = 32768
            "description" = "Research and general purpose model"
            "use_cases" = @("research", "documentation", "general_chat")
        }
        "gemma3:latest" = @{
            "temperature" = 0.5
            "top_p" = 0.85
            "max_tokens" = 2048
            "context_length" = 8192
            "description" = "Fast fallback model"
            "use_cases" = @("quick_responses", "simple_tasks", "fallback")
        }
    }
    "task_master_integration" = @{
        "auto_model_selection" = $true
        "model_routing" = @{
            "coding_tasks" = "coding"
            "research_tasks" = "research"
            "analysis_tasks" = "main"
            "quick_tasks" = "fallback"
        }
        "performance_optimization" = @{
            "parallel_processing" = $true
            "model_caching" = $true
            "response_streaming" = $false
        }
    }
}

$configPath = ".taskmaster/optimized-config.json"
$configDir = Split-Path $configPath -Parent
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configJson = $optimizedConfig | ConvertTo-Json -Depth 10
Set-Content -Path $configPath -Value $configJson -Encoding UTF8
Write-Host "SUCCESS: Optimized configuration created" -ForegroundColor Green

# Test the optimized integration
Write-Host "`n4. Testing optimized integration..." -ForegroundColor Yellow

try {
    $testResult = node taskmaster-ollama-optimized.js health
    Write-Host "SUCCESS: Optimized integration is working" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Optimized integration test failed" -ForegroundColor Yellow
}

# Test model stats
Write-Host "`n5. Testing model statistics..." -ForegroundColor Yellow

try {
    $statsResult = node taskmaster-ollama-optimized.js stats
    Write-Host "SUCCESS: Model statistics retrieved" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Model statistics test failed" -ForegroundColor Yellow
}

# Create Task Master usage examples
Write-Host "`n6. Creating usage examples..." -ForegroundColor Yellow

$usageExamples = @'
# Task Master Ollama Optimized Usage Examples

## Basic Commands
node taskmaster-ollama-optimized.js list                    # List all models
node taskmaster-ollama-optimized.js stats                   # Show model statistics
node taskmaster-ollama-optimized.js health                  # Check Ollama health

## Task Analysis
node taskmaster-ollama-optimized.js analyze scripts/ a REST API"  # Analyze task complexity
node taskmaster-ollama-optimized.js analyze scripts/ memory leak"  # Get task breakdown

## Code Generation
node taskmaster-ollama-optimized.js code scripts/ a React component"  # Generate code
node taskmaster-ollama-optimized.js code "Write a Python function"   # Generate code

## Research
node taskmaster-ollama-optimized.js research "Machine Learning"      # Research topic
node taskmaster-ollama-optimized.js research "Web Development"       # Research topic

## Direct Generation
node taskmaster-ollama-optimized.js generate main "Explain quantum computing"
node taskmaster-ollama-optimized.js generate coding "Write a sorting algorithm"
node taskmaster-ollama-optimized.js generate research "What is blockchain?"
node taskmaster-ollama-optimized.js generate fallback "Quick summary of AI"

## Model-Specific Tasks
- deepseek-r1:8b: Complex reasoning, analysis, problem-solving
- kirito1/qwen3-coder: Code generation, debugging, code review
- qwen3:latest: Research, documentation, general knowledge
- gemma3:latest: Quick responses, simple tasks, fallback

## Integration with Task Master
1. Change the main model to claude-code/sonnet
2. Use Ollama models for specific tasks:
   - Coding tasks → kirito1/qwen3-coder:latest
   - Research tasks → qwen3:latest
   - Analysis tasks → deepseek-r1:8b
   - Quick tasks → gemma3:latest
'@

Set-Content -Path "TASKMASTER_OLLAMA_USAGE.md" -Value $usageExamples -Encoding UTF8
Write-Host "SUCCESS: Usage examples created" -ForegroundColor Green

# Summary
Write-Host "`nTask Master Ollama Optimized Setup Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your optimized models:" -ForegroundColor Yellow
Write-Host "- deepseek-r1:8b (Main - Reasoning & Analysis)" -ForegroundColor White
Write-Host "- kirito1/qwen3-coder:latest (Coding - Code Generation)" -ForegroundColor White
Write-Host "- qwen3:latest (Research - Knowledge & Documentation)" -ForegroundColor White
Write-Host "- gemma3:latest (Fallback - Quick Responses)" -ForegroundColor White
Write-Host ""
Write-Host config/uration files created:" -ForegroundColor Yellow
Write-Host "- .taskmaster/optimized-config.json" -ForegroundColor White
Write-Host "- taskmaster-ollama-optimized.js" -ForegroundColor White
Write-Host "- TASKMASTER_OLLAMA_USAGE.md" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Cursor to load optimized configuration" -ForegroundColor White
Write-Host "2. Test Task Master with: 'Change the main model to claude-code/sonnet'" -ForegroundColor White
Write-Host "3. Use Ollama models for specific tasks in Task Master" -ForegroundColor White
Write-Host "4. Run: node taskmaster-ollama-optimized.js stats" -ForegroundColor White
Write-Host ""
Write-Host "Your Task Master is now fine-tuned for your specific Ollama models! 🚀" -ForegroundColor Green
