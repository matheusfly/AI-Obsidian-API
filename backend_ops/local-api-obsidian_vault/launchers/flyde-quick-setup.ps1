# 🚀 Flyde Quick Setup Script (PowerShell)
# Copy and paste this entire script to set up Flyde in seconds!

Write-Host "🚀 Setting up Flyde Development Environment..." -ForegroundColor Green

# Create project directory
$PROJECT_NAME = if ($args[0]) { $args[0] } else { "flyde-project" }
New-Item -ItemType Directory -Path $PROJECT_NAME -Force | Out-Null
Set-Location $PROJECT_NAME

# Initialize npm project
npm init -y

# Install Flyde dependencies
Write-Host "📦 Installing Flyde dependencies..." -ForegroundColor Blue
npm install @flyde/loader @flyde/nodes @flyde/runtime

# Install development dependencies
npm install --save-dev @flyde/cli @flyde/studio

# Create basic project structure
New-Item -ItemType Directory -Path "flows", "nodes", scripts/s", "examples" -Force | Out-Null

# Create sample flow
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

# Create package.json scripts
$packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
$packageJson | Add-Member -MemberType NoteProperty -Name "scripts" -Value @{
  "dev" = "flyde studio --port 3001 --open"
  "build" = "flyde build --output dist/"
  scripts/" = "flyde test"
  "run" = "flyde run flows/hello-world.flyde"
} -Force
$packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8

# Create flyde.config.js
$flydeConfig = @'
module.exports = {
  flowsDir: './flows',
  nodesDir: './nodes',
  outputDir: './dist',
  devServer: {
    port: 3001,
    host: 'localhost',
    open: true
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
'@

$flydeConfig | Out-File -FilePath "flyde.config.js" -Encoding UTF8

Write-Host "✅ Flyde environment setup complete!" -ForegroundColor Green
Write-Host "🎯 Quick commands:" -ForegroundColor Yellow
Write-Host "  npm run dev     - Launch Flyde Studio" -ForegroundColor Cyan
Write-Host "  npm run build   - Build flows" -ForegroundColor Cyan
Write-Host "  npm run test    - Run tests" -ForegroundColor Cyan
Write-Host "  npm run run     - Execute hello-world flow" -ForegroundColor Cyan
