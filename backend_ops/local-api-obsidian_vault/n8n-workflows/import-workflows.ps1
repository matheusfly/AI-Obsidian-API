#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Import and test Obsidian Q&A Chatbot workflows in n8n

.DESCRIPTION
    This script helps you import the Obsidian Q&A workflows into n8n and test them.

.PARAMETER WorkflowType
    Type of workflow to import: "simple", "complete", or "both"

.PARAMETER TestWorkflow
    Whether to test the workflow after import

.PARAMETER N8nUrl
    n8n base URL (default: http://localhost:5678)

.EXAMPLE
    .\import-workflows.ps1 -WorkflowType "simple" -TestWorkflow
    .\import-workflows.ps1 -WorkflowType "both" -N8nUrl "http://localhost:5678"
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("simple", "complete", "both")]
    [string]$WorkflowType = "simple",
    
    [Parameter(Mandatory = $false)]
    [switch]$TestWorkflow = $false,
    
    [Parameter(Mandatory = $false)]
    [string]$N8nUrl = "http://localhost:5678"
)

# Color definitions
$GREEN = "Green"
$BLUE = "Blue"
$YELLOW = "Yellow"
$RED = "Red"
$WHITE = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 OBSIDIAN Q&A CHATBOT WORKFLOW IMPORTER                ║
║                              n8n Integration Tool                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ $BLUE
}

function Test-N8nConnection {
    param([string]$Url)
    
    Write-ColorOutput "🔍 Testing n8n connection..." $BLUE
    
    try {
        $response = Invoke-RestMethod -Uri "$Url/healthz" -Method GET -TimeoutSec 10
        Write-ColorOutput "✅ n8n is running and accessible" $GREEN
        return $true
    }
    catch {
        Write-ColorOutput "❌ Cannot connect to n8n at $Url" $RED
        Write-ColorOutput "💡 Make sure n8n is running: docker-compose up n8n -d" $YELLOW
        return $false
    }
}

function Test-VaultApiConnection {
    Write-ColorOutput "🔍 Testing vault-api connection..." $BLUE
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET -TimeoutSec 10
        Write-ColorOutput "✅ vault-api is running and accessible" $GREEN
        return $true
    }
    catch {
        Write-ColorOutput "❌ Cannot connect to vault-api at http://localhost:8080" $RED
        Write-ColorOutput "💡 Make sure vault-api is running: docker-compose up vault-api -d" $YELLOW
        return $false
    }
}

function Import-Workflow {
    param(
        [string]$FilePath,
        [string]$WorkflowName,
        [string]$N8nBaseUrl
    )
    
    Write-ColorOutput "📥 Importing workflow: $WorkflowName" $BLUE
    
    if (-not (Test-Path $FilePath)) {
        Write-ColorOutput "❌ Workflow file not found: $FilePath" $RED
        return $false
    }
    
    try {
        # Read workflow JSON
        $workflowJson = Get-Content $FilePath -Raw
        
        # Import workflow via n8n API
        $importUrl = "$N8nBaseUrl/api/v1/workflows/import"
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        $body = @{
            "workflow" = $workflowJson | ConvertFrom-Json
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri $importUrl -Method POST -Body $body -Headers $headers
        
        Write-ColorOutput "✅ Workflow imported successfully: $WorkflowName" $GREEN
        Write-ColorOutput "   Workflow ID: $($response.id)" $WHITE
        return $true
    }
    catch {
        Write-ColorOutput "❌ Failed to import workflow: $($_.Exception.Message)" $RED
        return $false
    }
}

function Test-Workflow {
    param(
        [string]$WebhookPath,
        [string]$N8nBaseUrl
    )
    
    Write-ColorOutput "🧪 Testing workflow: $WebhookPath" $BLUE
    
    $webhookUrl = "$N8nBaseUrl/webhook/$WebhookPath"
    
    # Test data
    $testQuestions = @(
        @{
            question = "What files contain AI or agent information?"
            description = "AI/Agent search test"
        },
        @{
            question = "vault stats"
            description = "Vault statistics test"
        },
        @{
            question = "recent files"
            description = "Recent files test"
        }
    )
    
    foreach ($test in $testQuestions) {
        Write-ColorOutput "   Testing: $($test.description)" $YELLOW
        
        try {
            $body = @{
                question = $test.question
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
            
            if ($response.status -eq "success") {
                Write-ColorOutput "   ✅ $($test.description): SUCCESS" $GREEN
                if ($response.results) {
                    Write-ColorOutput "      Found $($response.results.Count) results" $WHITE
                }
            } else {
                Write-ColorOutput "   ⚠️  $($test.description): $($response.message)" $YELLOW
            }
        }
        catch {
            Write-ColorOutput "   ❌ $($test.description): $($_.Exception.Message)" $RED
        }
        
        Start-Sleep -Seconds 2
    }
}

function Show-WorkflowInfo {
    param([string]$N8nBaseUrl)
    
    Write-ColorOutput @"

🌐 Workflow Access Information:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📋 Simple Workflow:                                                        │
│    URL: $N8nBaseUrl/webhook/obsidian-simple                                │
│    Method: POST                                                             │
│    Body: {"question": "your question here"}                                │
│                                                                             │
│ 🤖 Complete Workflow:                                                      │
│    URL: $N8nBaseUrl/webhook/obsidian-qa                                    │
│    Method: POST                                                             │
│    Body: {"question": "your question here"}                                │
│                                                                             │
│ 🔧 n8n Interface:                                                          │
│    URL: $N8nBaseUrl                                                        │
│                                                                             │
│ 📊 Vault API:                                                              │
│    URL: http://localhost:8080                                               │
│    Health: http://localhost:8080/health                                     │
└─────────────────────────────────────────────────────────────────────────────┘

🧪 Quick Test Commands:
┌─────────────────────────────────────────────────────────────────────────────┐
│ # PowerShell Test:                                                         │
│ `$body = @{question = "What files contain AI?"} | ConvertTo-Json           │
│ Invoke-RestMethod -Uri "$N8nBaseUrl/webhook/obsidian-simple" `             │
│   -Method POST -Body `$body -ContentType "application/json"                │
│                                                                             │
│ # curl Test:                                                               │
│ curl -X POST $N8nBaseUrl/webhook/obsidian-simple `                         │
│   -H "Content-Type: application/json" `                                    │
│   -d '{"question": "What files contain AI?"}'                              │
└─────────────────────────────────────────────────────────────────────────────┘
"@ $BLUE
}

# Main execution
try {
    Write-Banner
    
    # Test connections
    Write-ColorOutput "🔍 Testing service connections..." $BLUE
    
    $n8nConnected = Test-N8nConnection -Url $N8nUrl
    $vaultApiConnected = Test-VaultApiConnection
    
    if (-not $n8nConnected) {
        Write-ColorOutput "❌ Cannot proceed without n8n connection" $RED
        exit 1
    }
    
    if (-not $vaultApiConnected) {
        Write-ColorOutput "⚠️  vault-api not connected - workflows may not work properly" $YELLOW
    }
    
    # Import workflows
    Write-ColorOutput "`n📥 Importing workflows..." $BLUE
    
    $importSuccess = @{}
    
    if ($WorkflowType -eq "simple" -or $WorkflowType -eq "both") {
        $importSuccess["simple"] = Import-Workflow -FilePath "obsidian-qa-simple.json" -WorkflowName "Obsidian Q&A Simple" -N8nBaseUrl $N8nUrl
    }
    
    if ($WorkflowType -eq "complete" -or $WorkflowType -eq "both") {
        $importSuccess["complete"] = Import-Workflow -FilePath "obsidian-qa-chatbot.json" -WorkflowName "Obsidian Q&A Complete" -N8nBaseUrl $N8nUrl
    }
    
    # Test workflows
    if ($TestWorkflow) {
        Write-ColorOutput "`n🧪 Testing workflows..." $BLUE
        
        if ($importSuccess["simple"]) {
            Test-Workflow -WebhookPath "obsidian-simple" -N8nBaseUrl $N8nUrl
        }
        
        if ($importSuccess["complete"]) {
            Test-Workflow -WebhookPath "obsidian-qa" -N8nBaseUrl $N8nUrl
        }
    }
    
    # Show results
    Write-ColorOutput "`n📊 Import Results:" $BLUE
    foreach ($workflow in $importSuccess.Keys) {
        $status = if ($importSuccess[$workflow]) { "✅ SUCCESS" } else { "❌ FAILED" }
        $color = if ($importSuccess[$workflow]) { $GREEN } else { $RED }
        Write-ColorOutput "   $workflow workflow: $status" $color
    }
    
    # Show usage information
    Show-WorkflowInfo -N8nBaseUrl $N8nUrl
    
    Write-ColorOutput "`n🎉 Workflow import completed!" $GREEN
    Write-ColorOutput "💡 Next steps:" $YELLOW
    Write-ColorOutput "   1. Go to n8n interface: $N8nUrl" $WHITE
    Write-ColorOutput "   2. Activate the imported workflows" $WHITE
    Write-ColorOutput "   3. Test with the provided commands" $WHITE
    
} catch {
    Write-ColorOutput "❌ Error: $($_.Exception.Message)" $RED
    exit 1
}
