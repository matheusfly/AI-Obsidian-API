# 🚀 Interactive CLI for Flyde & Motia Plugins (PowerShell)
# Master command-line interface for both visual programming tools

param(
    [string]$Command = "",
    [string]$SubCommand = "",
    [string]$Tool = "",
    [string]$ProjectName = "",
    [int]$Port = 0,
    [string]$Host = "localhost",
    [string]$Config = "",
    [string]$InputData = "",
    [string]$OutputFile = "",
    [switch]$Help,
    [switch]$Version,
    [switch]$Interactive
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
    Write-Host "🚀 Flyde & Motia Interactive CLI" -ForegroundColor $Colors.Magenta
    Write-Host "=================================" -ForegroundColor $Colors.Magenta
    Write-Host "Master command-line interface for visual programming tools" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "📚 Available Commands:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    Write-Host "🏗️  SETUP COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 setup flyde [project-name]     # Setup Flyde environment" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 setup motia [project-name]     # Setup Motia environment" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 setup both [project-name]      # Setup both environments" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🎨 LAUNCH COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 launch flyde [port] [host]     # Launch Flyde Studio" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 launch motia [port] [host]     # Launch Motia Dev Server" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 launch both [flyde-port] [motia-port] # Launch both tools" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🔄 EXECUTION COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 run flyde [flow-file] [input] [output] # Run Flyde flow" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 run motia [step-file] [input] [output] # Run Motia step" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🧪 TESTING COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 test flyde [flow-file]         # Test Flyde flow" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 test motia [step-file]         # Test Motia step" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 test all                       # Test all flows and steps" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "📦 BUILD COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 build flyde [output-dir]       # Build Flyde flows" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 build motia [output-dir]       # Build Motia steps" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 build all [output-dir]         # Build both tools" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🔍 ANALYSIS COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 analyze flyde [flow-file]      # Analyze Flyde flow" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 analyze motia [step-file]      # Analyze Motia step" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 analyze all                    # Analyze all components" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "📊 MONITORING COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 monitor flyde [endpoint]       # Monitor Flyde performance" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 monitor motia [endpoint]       # Monitor Motia performance" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 monitor all                    # Monitor both tools" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🚀 DEPLOYMENT COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 deploy flyde [target] [env]    # Deploy Flyde to cloud" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 deploy motia [target] [env]    # Deploy Motia to cloud" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 deploy all [target] [env]      # Deploy both tools" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "🔧 UTILITY COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\plugins.ps1 status                         # Show current status" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 clean                          # Clean build artifacts" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 update                         # Update dependencies" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 interactive                    # Enter interactive mode" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    Write-Host "📋 EXAMPLES:" -ForegroundColor $Colors.Yellow
    Write-Host "  .\plugins.ps1 setup flyde my-project         # Setup Flyde project" -ForegroundColor $Colors.White
    Write-Host "  .\plugins.ps1 launch both 3001 3000          # Launch both on custom ports" -ForegroundColor $Colors.White
    Write-Host "  .\plugins.ps1 run flyde flows/hello.flyde    # Run specific flow" -ForegroundColor $Colors.White
    Write-Host "  .\plugins.ps1 test all                       # Test everything" -ForegroundColor $Colors.White
    Write-Host "  .\plugins.ps1 build all dist/                # Build for production" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Version {
    Write-Host "🚀 Flyde & Motia Interactive CLI v1.0.0" -ForegroundColor $Colors.Green
    Write-Host "Built for Windows PowerShell" -ForegroundColor $Colors.White
    Write-Host ""
    
    # Check if tools are installed
    try {
        $flydeVersion = npx flyde --version 2>$null
        Write-Host "🎨 Flyde: $flydeVersion" -ForegroundColor $Colors.Cyan
    } catch {
        Write-Host "🎨 Flyde: Not installed" -ForegroundColor $Colors.Red
    }
    
    try {
        $motiaVersion = npx motia --version 2>$null
        Write-Host "⚡ Motia: $motiaVersion" -ForegroundColor $Colors.Cyan
    } catch {
        Write-Host "⚡ Motia: Not installed" -ForegroundColor $Colors.Red
    }
    Write-Host ""
}

function Show-Status {
    Write-Host "📊 Current Status:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    # Check if projects exist
    if (Test-Path "flyde-project" -PathType Container) {
        Write-Host "🎨 Flyde Project: ✅ Found" -ForegroundColor $Colors.Green
    } else {
        Write-Host "🎨 Flyde Project: ❌ Not found" -ForegroundColor $Colors.Red
    }
    
    if (Test-Path "motia-project" -PathType Container) {
        Write-Host "⚡ Motia Project: ✅ Found" -ForegroundColor $Colors.Green
    } else {
        Write-Host "⚡ Motia Project: ❌ Not found" -ForegroundColor $Colors.Red
    }
    
    # Check if tools are running
    $flydeProcess = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*flyde*" }
    if ($flydeProcess) {
        Write-Host "🎨 Flyde Studio: ✅ Running (PID: $($flydeProcess.Id))" -ForegroundColor $Colors.Green
    } else {
        Write-Host "🎨 Flyde Studio: ❌ Not running" -ForegroundColor $Colors.Red
    }
    
    $motiaProcess = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*motia*" }
    if ($motiaProcess) {
        Write-Host "⚡ Motia Dev Server: ✅ Running (PID: $($motiaProcess.Id))" -ForegroundColor $Colors.Green
    } else {
        Write-Host "⚡ Motia Dev Server: ❌ Not running" -ForegroundColor $Colors.Red
    }
    
    # Check port usage
    Write-Host ""
    Write-Host "🌐 Port Status:" -ForegroundColor $Colors.Yellow
    $ports = @(3000, 3001, 3002, 3003)
    foreach ($port in $ports) {
        $portStatus = netstat -an | findstr ":$port "
        if ($portStatus) {
            Write-Host "  Port ${port}: 🔴 In use" -ForegroundColor $Colors.Red
        } else {
            Write-Host "  Port ${port}: 🟢 Available" -ForegroundColor $Colors.Green
        }
    }
    Write-Host ""
}

function Setup-Flyde {
    param([string]$ProjectName = "flyde-project")
    
    Write-Host "🚀 Setting up Flyde environment..." -ForegroundColor $Colors.Green
    Write-Host "📁 Project: $ProjectName" -ForegroundColor $Colors.Blue
    
    if (Test-Path $ProjectName) {
        Write-Host "⚠️  Project directory already exists. Removing..." -ForegroundColor $Colors.Yellow
        Remove-Item $ProjectName -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $ProjectName -Force | Out-Null
    Set-Location $ProjectName
    
    # Initialize npm project
    npm init -y | Out-Null
    
    # Install dependencies
    Write-Host "📦 Installing Flyde dependencies..." -ForegroundColor $Colors.Blue
    npm install @flyde/loader @flyde/nodes @flyde/runtime | Out-Null
    npm install --save-dev @flyde/cli @flyde/studio | Out-Null
    
    # Create project structure
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
    
    # Update package.json
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $packageJson | Add-Member -MemberType NoteProperty -Name "scripts" -Value @{
        "dev" = "flyde studio --port 3001 --open"
        "build" = "flyde build --output dist/"
        scripts/" = "flyde test"
        "run" = "flyde run flows/hello-world.flyde"
    } -Force
    $packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
    
    # Create config
    $config = @'
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
    $config | Out-File -FilePath "flyde.config.js" -Encoding UTF8
    
    Set-Location ..
    Write-Host "✅ Flyde environment setup complete!" -ForegroundColor $Colors.Green
    Write-Host "🎯 Quick commands:" -ForegroundColor $Colors.Yellow
    Write-Host "  .\plugins.ps1 launch flyde    # Launch Flyde Studio" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 run flyde       # Run hello-world flow" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Setup-Motia {
    param([string]$ProjectName = "motia-project")
    
    Write-Host "⚡ Setting up Motia environment..." -ForegroundColor $Colors.Green
    Write-Host "📁 Project: $ProjectName" -ForegroundColor $Colors.Blue
    
    if (Test-Path $ProjectName) {
        Write-Host "⚠️  Project directory already exists. Removing..." -ForegroundColor $Colors.Yellow
        Remove-Item $ProjectName -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $ProjectName -Force | Out-Null
    Set-Location $ProjectName
    
    # Initialize npm project
    npm init -y | Out-Null
    
    # Install dependencies
    Write-Host "📦 Installing Motia dependencies..." -ForegroundColor $Colors.Blue
    npm install motia | Out-Null
    npm install --save-dev @types/node typescript ts-node | Out-Null
    
    # Create project structure
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
    
    # Update package.json
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $packageJson | Add-Member -MemberType NoteProperty -Name "scripts" -Value @{
        "dev" = "motia dev --port 3000 --open"
        "build" = "motia build --output dist/"
        scripts/" = "motia test"
        "run" = "motia run steps/hello-world.step.ts"
    } -Force
    $packageJson | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
    
    # Create config
    $config = @'
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
    $config | Out-File -FilePath "motia.config.js" -Encoding UTF8
    
    Set-Location ..
    Write-Host "✅ Motia environment setup complete!" -ForegroundColor $Colors.Green
    Write-Host "🎯 Quick commands:" -ForegroundColor $Colors.Yellow
    Write-Host "  .\plugins.ps1 launch motia    # Launch Motia Dev Server" -ForegroundColor $Colors.Cyan
    Write-Host "  .\plugins.ps1 run motia       # Run hello-world step" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Launch-Flyde {
    param([int]$Port = 3001, [string]$Host = "localhost")
    
    Write-Host "🎨 Launching Flyde Studio..." -ForegroundColor $Colors.Green
    Write-Host "📍 Port: $Port" -ForegroundColor $Colors.Blue
    Write-Host "🌐 Host: $Host" -ForegroundColor $Colors.Blue
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        if (Test-Path "flyde.config.js") {
            Write-Host "⚙️  Using flyde.config.js" -ForegroundColor $Colors.Blue
            npx flyde studio --config flyde.config.js --port $Port --host $Host --open
        } else {
            Write-Host "⚠️  No config found, using defaults" -ForegroundColor $Colors.Yellow
            npx flyde studio --port $Port --host $Host --open
        }
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Launch-Motia {
    param([int]$Port = 3000, [string]$Host = "localhost")
    
    Write-Host "⚡ Launching Motia Development Server..." -ForegroundColor $Colors.Green
    Write-Host "📍 Port: $Port" -ForegroundColor $Colors.Blue
    Write-Host "🌐 Host: $Host" -ForegroundColor $Colors.Blue
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        if (Test-Path "motia.config.js") {
            Write-Host "⚙️  Using motia.config.js" -ForegroundColor $Colors.Blue
            npx motia dev --config motia.config.js --port $Port --host $Host --open
        } else {
            Write-Host "⚠️  No config found, using defaults" -ForegroundColor $Colors.Yellow
            npx motia dev --port $Port --host $Host --open
        }
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Launch-Both {
    param([int]$FlydePort = 3001, [int]$MotiaPort = 3000)
    
    Write-Host "🚀 Launching Both Tools..." -ForegroundColor $Colors.Magenta
    Write-Host ""
    
    # Launch Motia in background
    Write-Host "⚡ Starting Motia on port $MotiaPort..." -ForegroundColor $Colors.Green
    Start-Process powershell -ArgumentList "-Command", ".\plugins.ps1 launch motia $MotiaPort" -WindowStyle Minimized
    
    # Wait a moment
    Start-Sleep -Seconds 3
    
    # Launch Flyde in foreground
    Write-Host "🎨 Starting Flyde on port $FlydePort..." -ForegroundColor $Colors.Green
    Launch-Flyde $FlydePort
}

function Run-Flyde {
    param([string]$FlowFile = "flows/hello-world.flyde", [string]$InputData = '{"message": "Hello from CLI!"}', [string]$OutputFile = "output.json")
    
    Write-Host "🔄 Executing Flyde Flow: $FlowFile" -ForegroundColor $Colors.Green
    Write-Host "📥 Input: $InputData" -ForegroundColor $Colors.Blue
    Write-Host "📤 Output: $OutputFile" -ForegroundColor $Colors.Blue
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        if (Test-Path $FlowFile) {
            npx flyde run $FlowFile --input $InputData --output $OutputFile
            Write-Host "✅ Flow execution complete!" -ForegroundColor $Colors.Green
            Write-Host "📄 Results saved to: $OutputFile" -ForegroundColor $Colors.Cyan
        } else {
            Write-Host "❌ Flow file not found: $FlowFile" -ForegroundColor $Colors.Red
        }
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Run-Motia {
    param([string]$StepFile = "steps/hello-world.step.ts", [string]$InputData = '{"message": "Hello from CLI!"}', [string]$OutputFile = "output.json")
    
    Write-Host "🔄 Executing Motia Step: $StepFile" -ForegroundColor $Colors.Green
    Write-Host "📥 Input: $InputData" -ForegroundColor $Colors.Blue
    Write-Host "📤 Output: $OutputFile" -ForegroundColor $Colors.Blue
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        if (Test-Path $StepFile) {
            npx motia run $StepFile --input $InputData --output $OutputFile
            Write-Host "✅ Step execution complete!" -ForegroundColor $Colors.Green
            Write-Host "📄 Results saved to: $OutputFile" -ForegroundColor $Colors.Cyan
        } else {
            Write-Host "❌ Step file not found: $StepFile" -ForegroundColor $Colors.Red
        }
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Test-Flyde {
    param([string]$FlowFile = "")
    
    Write-Host "🧪 Testing Flyde Flow: $FlowFile" -ForegroundColor $Colors.Green
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        if ($FlowFile -eq "") {
            npx flyde test
        } else {
            npx flyde test $FlowFile
        }
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Test-Motia {
    param([string]$StepFile = "")
    
    Write-Host "🧪 Testing Motia Step: $StepFile" -ForegroundColor $Colors.Green
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        if ($StepFile -eq "") {
            npx motia test
        } else {
            npx motia test $StepFile
        }
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Build-Flyde {
    param([string]$OutputDir = "dist")
    
    Write-Host "📦 Building Flyde Flows..." -ForegroundColor $Colors.Green
    Write-Host "📁 Output: $OutputDir" -ForegroundColor $Colors.Blue
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        npx flyde build --output $OutputDir
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Build-Motia {
    param([string]$OutputDir = "dist")
    
    Write-Host "📦 Building Motia Steps..." -ForegroundColor $Colors.Green
    Write-Host "📁 Output: $OutputDir" -ForegroundColor $Colors.Blue
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        npx motia build --output $OutputDir
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Analyze-Flyde {
    param([string]$FlowFile = "")
    
    Write-Host "🔍 Analyzing Flyde Flow: $FlowFile" -ForegroundColor $Colors.Green
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        if ($FlowFile -eq "") {
            npx flyde analyze flows/ --output analytics.json
        } else {
            npx flyde analyze $FlowFile --output analytics.json
        }
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Analyze-Motia {
    param([string]$StepFile = "")
    
    Write-Host "🔍 Analyzing Motia Step: $StepFile" -ForegroundColor $Colors.Green
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        if ($StepFile -eq "") {
            npx motia analyze steps/ --output analytics.json
        } else {
            npx motia analyze $StepFile --output analytics.json
        }
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Monitor-Flyde {
    param([string]$Endpoint = "http://localhost:3001")
    
    Write-Host "📊 Monitoring Flyde Performance..." -ForegroundColor $Colors.Green
    Write-Host "🌐 Endpoint: $Endpoint" -ForegroundColor $Colors.Blue
    
    npx flyde monitor --metrics cpu,memory,execution-time --endpoint $Endpoint
}

function Monitor-Motia {
    param([string]$Endpoint = "http://localhost:3000")
    
    Write-Host "📊 Monitoring Motia Performance..." -ForegroundColor $Colors.Green
    Write-Host "🌐 Endpoint: $Endpoint" -ForegroundColor $Colors.Blue
    
    npx motia monitor --metrics cpu,memory,execution-time --endpoint $Endpoint
}

function Deploy-Flyde {
    param([string]$Target = "vercel", [string]$Env = "production")
    
    Write-Host "🚀 Deploying Flyde to $Target..." -ForegroundColor $Colors.Green
    Write-Host "🌍 Environment: $Env" -ForegroundColor $Colors.Blue
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        npx flyde deploy --target $Target --env $Env
        Set-Location ..
    } else {
        Write-Host "❌ Flyde project not found. Run '.\plugins.ps1 setup flyde' first." -ForegroundColor $Colors.Red
    }
}

function Deploy-Motia {
    param([string]$Target = "vercel", [string]$Env = "production")
    
    Write-Host "🚀 Deploying Motia to $Target..." -ForegroundColor $Colors.Green
    Write-Host "🌍 Environment: $Env" -ForegroundColor $Colors.Blue
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        npx motia deploy --target $Target --env $Env
        Set-Location ..
    } else {
        Write-Host "❌ Motia project not found. Run '.\plugins.ps1 setup motia' first." -ForegroundColor $Colors.Red
    }
}

function Clean-All {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor $Colors.Green
    
    if (Test-Path "flyde-project/dist") {
        Remove-Item "flyde-project/dist" -Recurse -Force
        Write-Host "✅ Cleaned Flyde build artifacts" -ForegroundColor $Colors.Green
    }
    
    if (Test-Path "motia-project/dist") {
        Remove-Item "motia-project/dist" -Recurse -Force
        Write-Host "✅ Cleaned Motia build artifacts" -ForegroundColor $Colors.Green
    }
    
    Write-Host "✅ Cleanup complete!" -ForegroundColor $Colors.Green
}

function Update-Dependencies {
    Write-Host "🔄 Updating dependencies..." -ForegroundColor $Colors.Green
    
    if (Test-Path "flyde-project") {
        Set-Location "flyde-project"
        npm update
        Set-Location ..
        Write-Host "✅ Updated Flyde dependencies" -ForegroundColor $Colors.Green
    }
    
    if (Test-Path "motia-project") {
        Set-Location "motia-project"
        npm update
        Set-Location ..
        Write-Host "✅ Updated Motia dependencies" -ForegroundColor $Colors.Green
    }
    
    Write-Host "✅ Update complete!" -ForegroundColor $Colors.Green
}

function Start-Interactive {
    Write-Host "🎮 Entering Interactive Mode..." -ForegroundColor $Colors.Magenta
    Write-Host "Type 'help' for commands, 'exit' to quit" -ForegroundColor $Colors.White
    Write-Host ""
    
    while ($true) {
        $input = Read-Host "plugins> "
        $parts = $input -split " "
        
        if ($parts[0] -eq "exit" -or $parts[0] -eq "quit") {
            Write-Host "👋 Goodbye!" -ForegroundColor $Colors.Green
            break
        } elseif ($parts[0] -eq "help") {
            Show-Help
        } elseif ($parts[0] -eq "status") {
            Show-Status
        } elseif ($parts[0] -eq scripts/") {
            if ($parts[1] -eq "flyde") {
                Setup-Flyde $parts[2]
            } elseif ($parts[1] -eq "motia") {
                Setup-Motia $parts[2]
            } elseif ($parts[1] -eq "both") {
                Setup-Flyde $parts[2]
                Setup-Motia $parts[2]
            }
        } elseif ($parts[0] -eq "launch") {
            if ($parts[1] -eq "flyde") {
                Launch-Flyde $parts[2] $parts[3]
            } elseif ($parts[1] -eq "motia") {
                Launch-Motia $parts[2] $parts[3]
            } elseif ($parts[1] -eq "both") {
                Launch-Both $parts[2] $parts[3]
            }
        } elseif ($parts[0] -eq "run") {
            if ($parts[1] -eq "flyde") {
                Run-Flyde $parts[2] $parts[3] $parts[4]
            } elseif ($parts[1] -eq "motia") {
                Run-Motia $parts[2] $parts[3] $parts[4]
            }
        } elseif ($parts[0] -eq scripts/") {
            if ($parts[1] -eq "flyde") {
                Test-Flyde $parts[2]
            } elseif ($parts[1] -eq "motia") {
                Test-Motia $parts[2]
            } elseif ($parts[1] -eq "all") {
                Test-Flyde
                Test-Motia
            }
        } elseif ($parts[0] -eq "build") {
            if ($parts[1] -eq "flyde") {
                Build-Flyde $parts[2]
            } elseif ($parts[1] -eq "motia") {
                Build-Motia $parts[2]
            } elseif ($parts[1] -eq "all") {
                Build-Flyde $parts[2]
                Build-Motia $parts[2]
            }
        } elseif ($parts[0] -eq "analyze") {
            if ($parts[1] -eq "flyde") {
                Analyze-Flyde $parts[2]
            } elseif ($parts[1] -eq "motia") {
                Analyze-Motia $parts[2]
            } elseif ($parts[1] -eq "all") {
                Analyze-Flyde
                Analyze-Motia
            }
        } elseif ($parts[0] -eq scripts/") {
            if ($parts[1] -eq "flyde") {
                Monitor-Flyde $parts[2]
            } elseif ($parts[1] -eq "motia") {
                Monitor-Motia $parts[2]
            } elseif ($parts[1] -eq "all") {
                Monitor-Flyde
                Monitor-Motia
            }
        } elseif ($parts[0] -eq "deploy") {
            if ($parts[1] -eq "flyde") {
                Deploy-Flyde $parts[2] $parts[3]
            } elseif ($parts[1] -eq "motia") {
                Deploy-Motia $parts[2] $parts[3]
            } elseif ($parts[1] -eq "all") {
                Deploy-Flyde $parts[2] $parts[3]
                Deploy-Motia $parts[2] $parts[3]
            }
        } elseif ($parts[0] -eq "clean") {
            Clean-All
        } elseif ($parts[0] -eq "update") {
            Update-Dependencies
        } else {
            Write-Host "❌ Unknown command: $($parts[0])" -ForegroundColor $Colors.Red
            Write-Host "Type 'help' for available commands" -ForegroundColor $Colors.Yellow
        }
    }
}

# Main execution
Show-Banner

if ($Help) {
    Show-Help
} elseif ($Version) {
    Show-Version
} elseif ($Interactive) {
    Start-Interactive
} elseif ($Command -eq "status") {
    Show-Status
} elseif ($Command -eq scripts/") {
    if ($Tool -eq "flyde") {
        Setup-Flyde $ProjectName
    } elseif ($Tool -eq "motia") {
        Setup-Motia $ProjectName
    } elseif ($Tool -eq "both") {
        Setup-Flyde $ProjectName
        Setup-Motia $ProjectName
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or both" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "launch") {
    if ($Tool -eq "flyde") {
        Launch-Flyde $Port $Host
    } elseif ($Tool -eq "motia") {
        Launch-Motia $Port $Host
    } elseif ($Tool -eq "both") {
        Launch-Both $Port $SubCommand
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or both" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "run") {
    if ($Tool -eq "flyde") {
        Run-Flyde $SubCommand $InputData $OutputFile
    } elseif ($Tool -eq "motia") {
        Run-Motia $SubCommand $InputData $OutputFile
    } else {
        Write-Host "❌ Please specify tool: flyde or motia" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq scripts/") {
    if ($Tool -eq "flyde") {
        Test-Flyde $SubCommand
    } elseif ($Tool -eq "motia") {
        Test-Motia $SubCommand
    } elseif ($Tool -eq "all") {
        Test-Flyde
        Test-Motia
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or all" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "build") {
    if ($Tool -eq "flyde") {
        Build-Flyde $SubCommand
    } elseif ($Tool -eq "motia") {
        Build-Motia $SubCommand
    } elseif ($Tool -eq "all") {
        Build-Flyde $SubCommand
        Build-Motia $SubCommand
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or all" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "analyze") {
    if ($Tool -eq "flyde") {
        Analyze-Flyde $SubCommand
    } elseif ($Tool -eq "motia") {
        Analyze-Motia $SubCommand
    } elseif ($Tool -eq "all") {
        Analyze-Flyde
        Analyze-Motia
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or all" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq scripts/") {
    if ($Tool -eq "flyde") {
        Monitor-Flyde $SubCommand
    } elseif ($Tool -eq "motia") {
        Monitor-Motia $SubCommand
    } elseif ($Tool -eq "all") {
        Monitor-Flyde
        Monitor-Motia
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or all" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "deploy") {
    if ($Tool -eq "flyde") {
        Deploy-Flyde $SubCommand $InputData
    } elseif ($Tool -eq "motia") {
        Deploy-Motia $SubCommand $InputData
    } elseif ($Tool -eq "all") {
        Deploy-Flyde $SubCommand $InputData
        Deploy-Motia $SubCommand $InputData
    } else {
        Write-Host "❌ Please specify tool: flyde, motia, or all" -ForegroundColor $Colors.Red
    }
} elseif ($Command -eq "clean") {
    Clean-All
} elseif ($Command -eq "update") {
    Update-Dependencies
} else {
    Show-Help
}
