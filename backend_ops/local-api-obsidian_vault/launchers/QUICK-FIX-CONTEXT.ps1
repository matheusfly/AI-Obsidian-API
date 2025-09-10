# Quick Fix for Context Engineering Master
Write-Host "🔧 QUICK FIX - CONTEXT ENGINEERING MASTER" -ForegroundColor Cyan

# Create data directory
New-Item -ItemType Directory -Force -Path servicesservices/context-engineering-master\data\context" | Out-Null

# Create simple context data
$context = @{
    tools = @{
        "motia" = @{ name = "Motia Docs Scraper"; description = "Documentation scraper" }
        "chartdb" = @{ name = "ChartDB Visualizer"; description = data/base visualization" }
        "flyde" = @{ name = "Flyde Visual Flows"; description = "Visual programming" }
    }
    flows = @{
        "hello-world" = @{ name = "Hello World"; description = "Basic example flow" }
    }
    relationships = @{
        "motia-chartdb" = @{ type = data/-flow"; description = data/ flows from Motia to ChartDB" }
    }
}

$context | ConvertTo-Json -Depth 10 | Out-File -FilePath servicesservices/context-engineering-master\data\context\compressed-context.json" -Encoding UTF8

# Create simple server
$serverCode = @'
import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";
import cors from "cors";
import fs from "fs";
import path from "path";

const app = express();
const server = createServer(app);
const io = new Server(server, { cors: { origin: "*", methods: ["GET", "POST"] } });

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

let contextData = {};
try {
    const contextFile = path.join(process.cwd(), data/", "context", "compressed-context.json");
    contextData = JSON.parse(fs.readFileSync(contextFile, "utf8"));
} catch (error) {
    contextData = { tools: {}, flows: {}, relationships: {} };
}

app.get("/health", (req, res) => res.json({ status: "ok" }));
app.get("/api/context", (req, res) => res.json(contextData));
app.get("/api/tools", (req, res) => res.json(contextData.tools || {}));
app.get("/api/flows", (req, res) => res.json(contextData.flows || {}));

io.on("connection", (socket) => {
    console.log("Client connected:", socket.id);
    socket.emit("context-update", contextData);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log("🚀 Context Engineering Master started!");
    console.log("📱 Web UI: http://localhost:" + PORT);
    console.log("🔌 WebSocket: ws://localhost:" + PORT);
});
'@

$serverCode | Out-File -FilePath servicesservices/context-engineering-master\src\simple-server.js" -Encoding UTF8

# Update package.json
$packageJson = @{
    name = servicesservices/context-engineering-master"
    version = "1.0.0"
    type = "module"
    main = "src/simple-server.js"
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

Write-Host "✅ FIXED! Ready to launch:" -ForegroundColor Green
Write-Host "📱 .\LAUNCH-CONTEXT-MASTER-NOW.ps1" -ForegroundColor Yellow
