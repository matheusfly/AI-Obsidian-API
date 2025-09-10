# 🔧 Integration Issues Fix Script (PowerShell)
# Comprehensive fix for backend integration issues

param(
    [switch]$All,
    [switch]$Flyde,
    [switch]$Motia,
    [switch]$Backend,
    [switch]$Ports,
    [switch]$Help
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

function Show-Banner {
    Write-Host "🔧 Integration Issues Fix Script" -ForegroundColor $Colors.Magenta
    Write-Host "=================================" -ForegroundColor $Colors.Magenta
    Write-Host scripts/ing backend integration issues" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "📚 Available Fixes:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "🔧 FIX OPTIONS:" -ForegroundColor $Colors.Green
    Write-Host "  scripts/-integration-issues.ps1 -All        # Fix all issues" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-integration-issues.ps1 -Flyde      # Fix Flyde issues" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-integration-issues.ps1 -Motia      # Fix Motia issues" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-integration-issues.ps1 -Backend    # Fix backend issues" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-integration-issues.ps1 -Ports      # Fix port conflicts" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Fix-PortConflicts {
    Write-Host "🌐 Fixing Port Conflicts..." -ForegroundColor $Colors.Green
    
    # Kill processes on conflicting ports
    $conflictingPorts = @(3000, 3002, 8000, 8080, 5678)
    
    foreach ($port in $conflictingPorts) {
        Write-Host "🔍 Checking port $port..." -ForegroundColor $Colors.Blue
        
        try {
            $processes = netstat -ano | findstr ":$port "
            if ($processes) {
                Write-Host "  ⚠️  Port $port is in use" -ForegroundColor $Colors.Yellow
                
                # Extract PID and kill process
                $lines = $processes -split "`n"
                foreach ($line in $lines) {
                    if ($line -match '\s+(\d+)$') {
                        $pid = $matches[1]
                        Write-Host "  🛑 Killing process PID: $pid" -ForegroundColor $Colors.Yellow
                        try {
                            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                            Write-Host "  ✅ Process killed" -ForegroundColor $Colors.Green
                        } catch {
                            Write-Host "  ❌ Failed to kill process: $($_.Exception.Message)" -ForegroundColor $Colors.Red
                        }
                    }
                }
            } else {
                Write-Host "  ✅ Port $port is available" -ForegroundColor $Colors.Green
            }
        } catch {
            Write-Host "  ❌ Error checking port $port" -ForegroundColor $Colors.Red
        }
    }
    
    Write-Host ""
}

function Fix-FlydeIssues {
    Write-Host "🎨 Fixing Flyde Issues..." -ForegroundColor $Colors.Green
    
    # Remove existing flyde-project if it exists
    if (Test-Path "flyde-project") {
        Write-Host "🗑️  Removing existing flyde-project..." -ForegroundColor $Colors.Yellow
        Remove-Item "flyde-project" -Recurse -Force
    }
    
    # Create flyde-project directory
    Write-Host "📁 Creating flyde-project directory..." -ForegroundColor $Colors.Blue
    New-Item -ItemType Directory -Path "flyde-project" -Force | Out-Null
    Set-Location "flyde-project"
    
    # Initialize npm project
    Write-Host "📦 Initializing npm project..." -ForegroundColor $Colors.Blue
    npm init -y | Out-Null
    
    # Install Flyde dependencies
    Write-Host "📦 Installing Flyde dependencies..." -ForegroundColor $Colors.Blue
    npm install @flyde/loader @flyde/nodes @flyde/runtime --save
    npm install @flyde/cli @flyde/studio --save-dev
    
    # Create project structure
    Write-Host "📁 Creating project structure..." -ForegroundColor $Colors.Blue
    New-Item -ItemType Directory -Path "flows", "nodes", scripts/s", "examples" -Force | Out-Null
    
    # Create sample flow
    Write-Host "📝 Creating sample flow..." -ForegroundColor $Colors.Blue
    $sampleFlow = @'
imports: {}
node:
  instances:
    - id: start
      nodeId: InlineValue
      config:
        type: { type: string, value: "string" }
        value: { type: string, value: "Hello, Flyde!" }
    - id: output
      nodeId: Log
      config:
        message: "{{value}}"
  connections:
    - from: { insId: start, pinId: value }
      to: { insId: output, pinId: message }
'@
    
    $sampleFlow | Out-File -FilePath "flows/hello-world.flyde" -Encoding UTF8
    
    # Update package.json with scripts
    Write-Host "📝 Updating package.json..." -ForegroundColor $Colors.Blue
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $packageJson.scripts = @{
        "dev" = "flyde studio --port 3001 --open"
        "build" = "flyde build --output dist/"
        scripts/" = "flyde test"
        "run" = "flyde run flows/hello-world.flyde"
        "start" = "node server.js"
    }
    $packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
    
    # Create server.js for Docker
    Write-Host "📝 Creating server.js..." -ForegroundColor $Colors.Blue
    $serverJs = @'
const express = require('express');
const { runFlow } = require('@flyde/loader');
const path = require('path');

const app = express();
const PORT = process.env.FLYDE_PORT || 3001;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Run flow endpoint
app.post('/run/:flowName', async (req, res) => {
    try {
        const { flowName } = req.params;
        const input = req.body;
        
        const result = await runFlow(path.join(__dirname, 'flows', `${flowName}.flyde`), input);
        res.json({ success: true, result });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Flyde Studio running on port ${PORT}`);
});
'@
    
    $serverJs | Out-File -FilePath "server.js" -Encoding UTF8
    
    # Create config file
    Write-Host "📝 Creating flyde.config.js..." -ForegroundColor $Colors.Blue
    $config = @'
module.exports = {
  flowsDir: './flows',
  nodesDir: './nodes',
  outputDir: './dist',
  devServer: {
    port: 3001,
    host: '0.0.0.0',
    open: false
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
'@
    $config | Out-File -FilePath "flyde.config.js" -Encoding UTF8
    
    Set-Location ..
    Write-Host "✅ Flyde project setup complete!" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Fix-MotiaIssues {
    Write-Host "⚡ Fixing Motia Issues..." -ForegroundColor $Colors.Green
    
    # Remove existing motia-project if it exists
    if (Test-Path "motia-project") {
        Write-Host "🗑️  Removing existing motia-project..." -ForegroundColor $Colors.Yellow
        Remove-Item "motia-project" -Recurse -Force
    }
    
    # Create motia-project directory
    Write-Host "📁 Creating motia-project directory..." -ForegroundColor $Colors.Blue
    New-Item -ItemType Directory -Path "motia-project" -Force | Out-Null
    Set-Location "motia-project"
    
    # Initialize npm project
    Write-Host "📦 Initializing npm project..." -ForegroundColor $Colors.Blue
    npm init -y | Out-Null
    
    # Install Motia dependencies
    Write-Host "📦 Installing Motia dependencies..." -ForegroundColor $Colors.Blue
    npm install motia --save
    npm install @types/node typescript ts-node --save-dev
    
    # Create project structure
    Write-Host "📁 Creating project structure..." -ForegroundColor $Colors.Blue
    New-Item -ItemType Directory -Path "steps", "workflows", scripts/s", "examples" -Force | Out-Null
    
    # Create sample step
    Write-Host "📝 Creating sample step..." -ForegroundColor $Colors.Blue
    $sampleStep = @'
import { StepConfig, Handlers } from 'motia'

export const config: StepConfig = {
  type: 'api',
  name: 'HelloWorld',
  description: 'Simple hello world step',
  method: 'GET',
  path: '/hello',
  responseSchema: {
    200: {
      type: 'object',
      properties: {
        message: { type: 'string' },
        timestamp: { type: 'string' }
      }
    }
  }
}

export const handler: Handlers['ApiTrigger'] = async (req, { logger }) => {
  logger.info('Hello World step executed')
  
  return {
    status: 200,
    body: {
      message: 'Hello, Motia!',
      timestamp: new Date().toISOString()
    }
  }
}
'@
    
    $sampleStep | Out-File -FilePath "steps/hello-world.step.ts" -Encoding UTF8
    
    # Update package.json with scripts
    Write-Host "📝 Updating package.json..." -ForegroundColor $Colors.Blue
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $packageJson.scripts = @{
        "dev" = "motia dev --port 3000 --open"
        "build" = "motia build --output dist/"
        scripts/" = "motia test"
        "run" = "motia run steps/hello-world.step.ts"
        "start" = "node server.js"
    }
    $packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
    
    # Create server.js for Docker
    Write-Host "📝 Creating server.js..." -ForegroundColor $Colors.Blue
    $serverJs = @'
const express = require('express');
const { runStep } = require('motia');

const app = express();
const PORT = process.env.MOTIA_PORT || 3000;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Run step endpoint
app.post('/run/:stepName', async (req, res) => {
    try {
        const { stepName } = req.params;
        const input = req.body;
        
        const result = await runStep(`steps/${stepName}.step.ts`, input);
        res.json({ success: true, result });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Motia Dev Server running on port ${PORT}`);
});
'@
    
    $serverJs | Out-File -FilePath "server.js" -Encoding UTF8
    
    # Create config file
    Write-Host "📝 Creating motia.config.js..." -ForegroundColor $Colors.Blue
    $config = @'
module.exports = {
  stepsDir: './steps',
  workflowsDir: './workflows',
  outputDir: './dist',
  devServer: {
    port: 3000,
    host: '0.0.0.0',
    open: false
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
'@
    $config | Out-File -FilePath "motia.config.js" -Encoding UTF8
    
    Set-Location ..
    Write-Host "✅ Motia project setup complete!" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Fix-BackendIssues {
    Write-Host "🔗 Fixing Backend Issues..." -ForegroundColor $Colors.Green
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "📝 Creating .env file..." -ForegroundColor $Colors.Blue
        $envContent = @"
# Backend Integration Environment Variables
# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_123
POSTGRES_NON_ROOT_USER=n8n_user
POSTGRES_NON_ROOT_PASSWORD=n8n_password_123

# Redis Configuration
REDIS_PASSWORD=redis_password_123

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin_password_123
N8N_ENCRYPTION_KEY=your_encryption_key_here

# Obsidian API Configuration
OBSIDIAN_API_KEY=your_obsidian_api_key_here

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=grafana_password_123

# Security
JWT_SECRET=your_jwt_secret_here
API_SECRET=your_api_secret_here
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ .env file created" -ForegroundColor $Colors.Green
    }
    
    # Create monitoring directory
    if (-not (Test-Path monitoring/")) {
        Write-Host "📁 Creating monitoring directory..." -ForegroundColor $Colors.Blue
        New-Item -ItemType Directory -Path monitoring/" -Force | Out-Null
    }
    
    # Create nginx directory
    if (-not (Test-Path servicesservices/nginx")) {
        Write-Host "📁 Creating nginx directory..." -ForegroundColor $Colors.Blue
        New-Item -ItemType Directory -Path servicesservices/nginx" -Force | Out-Null
    }
    
    Write-Host "✅ Backend issues fixed!" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Test-Integration {
    Write-Host "🧪 Testing Integration..." -ForegroundColor $Colors.Green
    
    # Test Flyde
    if (Test-Path "flyde-project") {
        Write-Host "🎨 Testing Flyde..." -ForegroundColor $Colors.Blue
        Set-Location "flyde-project"
        try {
            $result = npm run run 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Flyde test successful" -ForegroundColor $Colors.Green
            } else {
                Write-Host "  ❌ Flyde test failed: $result" -ForegroundColor $Colors.Red
            }
        } catch {
            Write-Host "  ❌ Flyde test error: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        }
        Set-Location ..
    }
    
    # Test Motia
    if (Test-Path "motia-project") {
        Write-Host "⚡ Testing Motia..." -ForegroundColor $Colors.Blue
        Set-Location "motia-project"
        try {
            $result = npm run run 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Motia test successful" -ForegroundColor $Colors.Green
            } else {
                Write-Host "  ❌ Motia test failed: $result" -ForegroundColor $Colors.Red
            }
        } catch {
            Write-Host "  ❌ Motia test error: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        }
        Set-Location ..
    }
    
    Write-Host ""
}

# Main execution
Show-Banner

if ($Help) {
    Show-Help
} else {
    if ($All -or $Ports) {
        Fix-PortConflicts
    }
    
    if ($All -or $Flyde) {
        Fix-FlydeIssues
    }
    
    if ($All -or $Motia) {
        Fix-MotiaIssues
    }
    
    if ($All -or $Backend) {
        Fix-BackendIssues
    }
    
    if ($All) {
        Test-Integration
    }
    
    Write-Host "🎉 Integration fixes completed!" -ForegroundColor $Colors.Green
    Write-Host "Run '.\backend-integration-test.ps1 all' to test the integration" -ForegroundColor $Colors.Cyan
}
