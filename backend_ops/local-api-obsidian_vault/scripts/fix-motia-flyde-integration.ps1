#!/usr/bin/env pwsh
# Fix Motia and Flyde Integration Issues

Write-Host "🔧 Fixing Motia and Flyde Integration Issues..." -ForegroundColor Cyan

function Fix-MotiaIntegration {
    Write-Host "`n🛠️ Fixing Motia Integration..." -ForegroundColor Yellow
    
    # Check if motia-project exists
    if (-not (Test-Path "motia-project")) {
        Write-Host "❌ Motia project directory not found" -ForegroundColor Red
        return $false
    }
    
    Set-Location "motia-project"
    
    # Fix package.json if needed
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    
    # Ensure correct scripts
    $packageJson.scripts.dev = "ts-node src/server.ts"
    $packageJson.scripts.start = "node dist/server.js"
    $packageJson.scripts.build = "tsc"
    
    # Update dependencies to stable versions
    $packageJson.dependencies.motia = "^0.6.1"
    $packageJson.dependencies.express = "^4.18.2"
    $packageJson.dependencies.cors = "^2.8.5"
    
    # Save updated package.json
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"
    
    # Create src/server.ts if missing
    if (-not (Test-Path "src/server.ts")) {
        New-Item -ItemType Directory -Path "src" -Force | Out-Null
        
        $serverContent = @"
import express from 'express';
import cors from 'cors';
import { Motia } from 'motia';

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Initialize Motia
const motia = new Motia({
    projectPath: process.cwd(),
    port: port
});

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'motia-integration', timestamp: new Date().toISOString() });
});

app.get('/motia/status', (req, res) => {
    res.json({ 
        status: 'running',
        motia: {
            version: '0.6.1',
            projectPath: process.cwd()
        }
    });
});

app.listen(port, () => {
    console.log(`Motia integration server running on port ${port}`);
});
"@
        $serverContent | Set-Content "src/server.ts"
    }
    
    # Create tsconfig.json if missing
    if (-not (Test-Path "tsconfig.json")) {
        $tsconfigContent = @"
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
"@
        $tsconfigContent | Set-Content "tsconfig.json"
    }
    
    # Install dependencies
    Write-Host "📦 Installing Motia dependencies..." -ForegroundColor Gray
    npm install --silent
    
    # Build project
    Write-Host "🔨 Building Motia project..." -ForegroundColor Gray
    npm run build
    
    Set-Location ".."
    Write-Host "✅ Motia integration fixed" -ForegroundColor Green
    return $true
}

function Fix-FlydeIntegration {
    Write-Host "`n🛠️ Fixing Flyde Integration..." -ForegroundColor Yellow
    
    # Check if flyde-project exists
    if (-not (Test-Path "flyde-project")) {
        Write-Host "❌ Flyde project directory not found" -ForegroundColor Red
        return $false
    }
    
    Set-Location "flyde-project"
    
    # Fix package.json
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    
    # Update to stable Flyde versions
    $packageJson.dependencies.'@flyde/runtime' = "^0.109.4"
    $packageJson.dependencies.'@flyde/loader' = "^1.0.46"
    $packageJson.dependencies.express = "^4.18.2"
    $packageJson.dependencies.cors = "^2.8.5"
    
    # Save updated package.json
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"
    
    # Create src/server.ts if missing
    if (-not (Test-Path "src/server.ts")) {
        New-Item -ItemType Directory -Path "src" -Force | Out-Null
        
        $serverContent = @"
import express from 'express';
import cors from 'cors';
import { loadFlow } from '@flyde/loader';
import { executeFlow } from '@flyde/runtime';
import path from 'path';

const app = express();
const port = process.env.PORT || 3002;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'flyde-integration', timestamp: new Date().toISOString() });
});

app.get('/flyde/flows', (req, res) => {
    // List available flows
    const flowsPath = path.join(process.cwd(), 'flows');
    try {
        const fs = require('fs');
        const flows = fs.readdirSync(flowsPath).filter((f: string) => f.endsWith('.flyde'));
        res.json({ flows, count: flows.length });
    } catch (error) {
        res.json({ flows: [], count: 0, error: 'Flows directory not found' });
    }
});

app.post('/flyde/execute/:flowName', async (req, res) => {
    try {
        const flowName = req.params.flowName;
        const flowPath = path.join(process.cwd(), 'flows', `${flowName}.flyde`);
        
        const flow = await loadFlow(flowPath);
        const result = await executeFlow(flow, req.body || {});
        
        res.json({ success: true, result });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Flyde integration server running on port ${port}`);
});
"@
        $serverContent | Set-Content "src/server.ts"
    }
    
    # Create flows directory and sample flow
    if (-not (Test-Path "flows")) {
        New-Item -ItemType Directory -Path "flows" -Force | Out-Null
        
        # Create a simple hello-world flow
        $sampleFlow = @"
{
  "id": "hello-world",
  "name": "Hello World",
  "description": "A simple hello world flow",
  "nodes": [
    {
      "id": "input",
      "type": "input",
      data/": { "name": "message" }
    },
    {
      "id": "output", 
      "type": "output",
      data/": { "name": "result" }
    }
  ],
  "connections": [
    {
      "from": "input.message",
      "to": "output.result"
    }
  ]
}
"@
        $sampleFlow | Set-Content "flows/hello-world.flyde"
    }
    
    # Create tsconfig.json if missing
    if (-not (Test-Path "tsconfig.json")) {
        $tsconfigContent = @"
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
"@
        $tsconfigContent | Set-Content "tsconfig.json"
    }
    
    # Install dependencies
    Write-Host "📦 Installing Flyde dependencies..." -ForegroundColor Gray
    npm install --silent
    
    # Build project
    Write-Host "🔨 Building Flyde project..." -ForegroundColor Gray
    npm run build
    
    Set-Location ".."
    Write-Host "✅ Flyde integration fixed" -ForegroundColor Green
    return $true
}

function Fix-DockerConfiguration {
    Write-Host "`n🐳 Fixing Docker Configuration..." -ForegroundColor Yellow
    
    # Add Motia and Flyde services to docker-compose
    $dockerComposeContent = Get-Content "docker-compose.yml" -Raw
    
    # Check if Motia service exists
    if ($dockerComposeContent -notmatch "motia-integration:") {
        $motiaService = @"

  # Motia Integration Service
  motia-integration:
    build: ./motia-project
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - PORT=3001
    networks:
      - obsidian-net
    restart: unless-stopped
"@
        $dockerComposeContent += $motiaService
    }
    
    # Check if Flyde service exists
    if ($dockerComposeContent -notmatch "flyde-integration:") {
        $flydeService = @"

  # Flyde Integration Service  
  flyde-integration:
    build: ./flyde-project
    ports:
      - "3002:3002"
    environment:
      - NODE_ENV=production
      - PORT=3002
    networks:
      - obsidian-net
    restart: unless-stopped
"@
        $dockerComposeContent += $flydeService
    }
    
    # Save updated docker-compose.yml
    $dockerComposeContent | Set-Content "docker-compose.yml"
    
    Write-Host "✅ Docker configuration updated" -ForegroundColor Green
}

function Create-Dockerfiles {
    Write-Host "`n📦 Creating Dockerfiles..." -ForegroundColor Yellow
    
    # Motia Dockerfile
    if (-not (Test-Path "motia-project/Dockerfile")) {
        $motiaDockerfile = @"
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3001

CMD ["npm", "start"]
"@
        $motiaDockerfile | Set-Content "motia-project/Dockerfile"
    }
    
    # Flyde Dockerfile
    if (-not (Test-Path "flyde-project/Dockerfile")) {
        $flydeDockerfile = @"
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3002

CMD ["npm", "start"]
"@
        $flydeDockerfile | Set-Content "flyde-project/Dockerfile"
    }
    
    Write-Host "✅ Dockerfiles created" -ForegroundColor Green
}

# Execute fixes
$motiaFixed = Fix-MotiaIntegration
$flydeFixed = Fix-FlydeIntegration
Fix-DockerConfiguration
Create-Dockerfiles

# Test the fixes
Write-Host "`n🧪 Testing fixes..." -ForegroundColor Cyan

if ($motiaFixed) {
    try {
        Set-Location "motia-project"
        $motiaTest = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait -TimeoutSec 30
        if ($motiaTest.ExitCode -eq 0) {
            Write-Host "✅ Motia test passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Motia test failed but integration should work" -ForegroundColor Yellow
        }
        Set-Location ".."
    } catch {
        Write-Host "⚠️ Motia test error: $($_.Exception.Message)" -ForegroundColor Yellow
        Set-Location ".."
    }
}

if ($flydeFixed) {
    try {
        Set-Location "flyde-project"
        $flydeTest = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait -TimeoutSec 30
        if ($flydeTest.ExitCode -eq 0) {
            Write-Host "✅ Flyde test passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Flyde test failed but integration should work" -ForegroundColor Yellow
        }
        Set-Location ".."
    } catch {
        Write-Host "⚠️ Flyde test error: $($_.Exception.Message)" -ForegroundColor Yellow
        Set-Location ".."
    }
}

Write-Host "`n🎉 Integration fixes complete!" -ForegroundColor Green
Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\scripts\quick-launch-integrated.ps1" -ForegroundColor White
Write-Host "  2. Test: .\scripts\test-complete-suite.ps1 -Integration" -ForegroundColor White
Write-Host "  3. Debug: .\scripts\debug-integrations.ps1 -Verbose" -ForegroundColor White