# 🚀 Motia Quick Setup Script (PowerShell)
# Copy and paste this entire script to set up Motia in seconds!

Write-Host "⚡ Setting up Motia Development Environment..." -ForegroundColor Green

# Create project directory
$PROJECT_NAME = if ($args[0]) { $args[0] } else { "motia-project" }
New-Item -ItemType Directory -Path $PROJECT_NAME -Force | Out-Null
Set-Location $PROJECT_NAME

# Initialize npm project
npm init -y

# Install Motia dependencies
Write-Host "📦 Installing Motia dependencies..." -ForegroundColor Blue
npm install motia

# Install development dependencies
npm install --save-dev @types/node typescript ts-node

# Create basic project structure
New-Item -ItemType Directory -Path "steps", "workflows", scripts/s", "examples" -Force | Out-Null

# Create sample step
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

# Create package.json scripts
$packageJsonScripts = @'
  "scripts": {
    "dev": "motia dev --port 3000 --open",
    "build": "motia build --output dist/",
    scripts/": "motia test",
    "run": "motia run steps/hello-world.step.ts"
  }
'@

# Read current package.json and add scripts
$packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
$packageJson | Add-Member -MemberType NoteProperty -Name "scripts" -Value @{
  "dev" = "motia dev --port 3000 --open"
  "build" = "motia build --output dist/"
  scripts/" = "motia test"
  "run" = "motia run steps/hello-world.step.ts"
} -Force
$packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8

# Create motia.config.js
$motiaConfig = @'
module.exports = {
  stepsDir: './steps',
  workflowsDir: './workflows',
  outputDir: './dist',
  devServer: {
    port: 3000,
    host: 'localhost',
    open: true
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
'@

$motiaConfig | Out-File -FilePath "motia.config.js" -Encoding UTF8

Write-Host "✅ Motia environment setup complete!" -ForegroundColor Green
Write-Host "🎯 Quick commands:" -ForegroundColor Yellow
Write-Host "  npm run dev     - Launch Motia Dev Server" -ForegroundColor Cyan
Write-Host "  npm run build   - Build steps" -ForegroundColor Cyan
Write-Host "  npm run test    - Run tests" -ForegroundColor Cyan
Write-Host "  npm run run     - Execute hello-world step" -ForegroundColor Cyan
