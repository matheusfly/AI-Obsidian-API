# Fix Context Engineering Master
# Quick fix for all issues

Write-Host "🔧 FIXING CONTEXT ENGINEERING MASTER..." -ForegroundColor Cyan

# Fix 1: Create data directory
Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path servicesservices/context-engineering-master\data\context" | Out-Null

# Fix 2: Create simple context compression without Supabase
Write-Host "🧠 Creating simplified context engine..." -ForegroundColor Yellow
$simpleContext = @{
    tools = @{
        "motia-docs-scraper" = @{
            name = "Motia Docs Scraper"
            description = "Documentation scraper for Motia framework"
            capabilities = @("scrape", "parse", "extract")
        }
        "chartdb-docs-scraper" = @{
            name = "ChartDB Docs Scraper" 
            description = data/base visualization tool"
            capabilities = @("visualize", "diagram", "schema")
        }
        servicesservices/flyde-mcp-project" = @{
            name = "Flyde Visual Flows"
            description = "Visual programming interface"
            capabilities = @("visual", "flow", "programming")
        }
    }
    flows = @{
        "hello-world" = @{
            name = "Hello World Flow"
            description = "Basic example flow"
            nodes = @("input", "process", "output")
        }
    }
    relationships = @{
        "motia-chartdb" = @{
            type = data/-flow"
            description = "Motia provides data to ChartDB"
        }
    }
}

# Save to local file
$contextFile = servicesservices/context-engineering-master\data\context\compressed-context.json"
$simpleContext | ConvertTo-Json -Depth 10 | Out-File -FilePath $contextFile -Encoding UTF8

Write-Host "✅ Context data created locally" -ForegroundColor Green

# Fix 3: Create simple server without Supabase dependency
Write-Host "🚀 Creating simplified server..." -ForegroundColor Yellow
$simpleServer = @'
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import fs from 'fs';
import path from 'path';

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Load context data
let contextData = null;
try {
    const contextFile = path.join(process.cwd(), data/', 'context', 'compressed-context.json');
    contextData = JSON.parse(fs.readFileSync(contextFile, 'utf8'));
    console.log('✅ Context data loaded');
} catch (error) {
    console.log('⚠️ Using default context data');
    contextData = {
        tools: {},
        flows: {},
        relationships: {}
    };
}

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.get('/api/context', (req, res) => {
    res.json(contextData);
});

app.get('/api/tools', (req, res) => {
    res.json(contextData.tools || {});
});

app.get('/api/flows', (req, res) => {
    res.json(contextData.flows || {});
});

app.get('/api/relationships', (req, res) => {
    res.json(contextData.relationships || {});
});

// WebSocket connection
io.on('connection', (socket) => {
    console.log('🔌 Client connected:', socket.id);
    
    socket.emit('context-update', contextData);
    
    socket.on('disconnect', () => {
        console.log('🔌 Client disconnected:', socket.id);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log('🚀 Context Engineering Master started!');
    console.log('📱 Web UI: http://localhost:' + PORT);
    console.log('🔌 WebSocket: ws://localhost:' + PORT);
    console.log('📊 API: http://localhost:' + PORT + '/api');
});
'@

$simpleServer | Out-File -FilePath servicesservices/context-engineering-master\src\simple-server.js" -Encoding UTF8

Write-Host "✅ Simple server created" -ForegroundColor Green

# Fix 4: Update package.json to use simple server
Write-Host "📦 Updating package.json..." -ForegroundColor Yellow
$packageJson = @{
    name = servicesservices/context-engineering-master"
    version = "1.0.0"
    description = "Unified Knowledge Compression and Interactive Visual Programming"
    main = "src/simple-server.js"
    type = "module"
    scripts = @{
        start = "node src/simple-server.js"
        dev = "node src/simple-server.js"
    }
    dependencies = @{
        express = "^4.18.0"
        "socket.io" = "^4.7.0"
        cors = "^2.8.5"
    }
} | ConvertTo-Json -Depth 10

$packageJson | Out-File -FilePath servicesservices/context-engineering-master\package.json" -Encoding UTF8

Write-Host "✅ Package.json updated" -ForegroundColor Green

# Fix 5: Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
Set-Location servicesservices/context-engineering-master"
npm install
Set-Location ".."

Write-Host "✅ Dependencies installed" -ForegroundColor Green

Write-Host "`n🎉 CONTEXT ENGINEERING MASTER FIXED!" -ForegroundColor Green
Write-Host "📱 Ready to launch: .\LAUNCH-CONTEXT-MASTER-NOW.ps1" -ForegroundColor Cyan
Write-Host "🧪 Test: scripts/-CONTEXT-MASTER.ps1" -ForegroundColor Yellow
