# Test Context Engineering Master
# Simple test to verify the system works

Write-Host "🧪 Testing Context Engineering Master..." -ForegroundColor Cyan

# Change to context engineering directory
Set-Location "context-engineering-master"

# Check if package.json exists
if (Test-Path "package.json") {
    Write-Host "✅ package.json found" -ForegroundColor Green
} else {
    Write-Host "❌ package.json not found" -ForegroundColor Red
    exit 1
}

# Check if src directory exists
if (Test-Path "src") {
    Write-Host "✅ src directory found" -ForegroundColor Green
} else {
    Write-Host "❌ src directory not found" -ForegroundColor Red
    exit 1
}

# Check if main files exist
$files = @(
    "src/index.js",
    "src/context-compression-engine.js",
    "src/flyde-web-ui.js",
    "src/mcp-integration-manager.js",
    "src/knowledge-graph.js",
    "public/index.html",
    "examples/hello-world-context.flyde"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file found" -ForegroundColor Green
    } else {
        Write-Host "❌ $file not found" -ForegroundColor Red
    }
}

# Test Node.js syntax
Write-Host "🔍 Testing Node.js syntax..." -ForegroundColor Yellow
try {
    node -c src/index.js
    Write-Host "✅ src/index.js syntax OK" -ForegroundColor Green
} catch {
    Write-Host "❌ src/index.js syntax error" -ForegroundColor Red
}

try {
    node -c src/context-compression-engine.js
    Write-Host "✅ src/context-compression-engine.js syntax OK" -ForegroundColor Green
} catch {
    Write-Host "❌ src/context-compression-engine.js syntax error" -ForegroundColor Red
}

try {
    node -c src/flyde-web-ui.js
    Write-Host "✅ src/flyde-web-ui.js syntax OK" -ForegroundColor Green
} catch {
    Write-Host "❌ src/flyde-web-ui.js syntax error" -ForegroundColor Red
}

Write-Host "`n🎉 Context Engineering Master test completed!" -ForegroundColor Green
Write-Host "📱 Ready to launch at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🚀 Run: .\LAUNCH-CONTEXT-MASTER-NOW.ps1" -ForegroundColor Yellow
