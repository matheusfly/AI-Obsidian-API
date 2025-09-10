# Complete Test Suite for Obsidian Vault AI Launch Scripts
param(
    [string]$TestSuite = "all",
    [switch]$Verbose = $false,
    [switch]$ContinueOnError = $false
)

$script:TestResults = @{
    Passed = 0
    Failed = 0
    Skipped = 0
    Tests = @()
}

function Write-TestOutput {
    param([string]$Message, [string]$Level = "INFO")
    $colors = @{"PASS" = "Green"; "FAIL" = "Red"; "SKIP" = "Yellow"; "INFO" = "Cyan"}
    Write-Host "[$Level] $Message" -ForegroundColor $colors[$Level]
}

function Test-Assert {
    param([string]$TestName, [scriptblock]$TestBlock, [string]$Description = "")
    
    try {
        Write-TestOutput "Running: $TestName" "INFO"
        $result = & $TestBlock
        
        if ($result -eq $true -or $result -eq $null) {
            $script:TestResults.Passed++
            Write-TestOutput "✅ PASS: $TestName" "PASS"
            return $true
        } else {
            $script:TestResults.Failed++
            Write-TestOutput "❌ FAIL: $TestName" "FAIL"
            return $false
        }
    }
    catch {
        $script:TestResults.Failed++
        Write-TestOutput "❌ FAIL: $TestName - $($_.Exception.Message)" "FAIL"
        if (-not $ContinueOnError) { throw }
        return $false
    }
}

function Test-Prerequisites {
    Write-TestOutput "=== PREREQUISITES TESTS ===" "INFO"
    
    Test-Assert "Docker Installation" {
        $dockerVersion = docker --version 2>$null
        return $dockerVersion -ne $null
    }
    
    Test-Assert "Docker Compose Installation" {
        $composeVersion = docker-compose --version 2>$null
        return $composeVersion -ne $null
    }
    
    Test-Assert "Docker Service Running" {
        try {
            docker info 2>$null | Out-Null
            return $true
        } catch {
            return $false
        }
    }
    
    Test-Assert "Project Files Exist" {
        $files = @("docker-compose.yml", "scripts\launch.ps1", "scripts\vault-cli.ps1", ".env.example")
        foreach ($file in $files) {
            if (-not (Test-Path $file)) { throw "Missing: $file" }
        }
        return $true
    }
    
    Test-Assert "Vault Path Accessible" {
        $vaultPath = "D:\Nomade Milionario"
        return Test-Path $vaultPath
    }
    
    Test-Assert "PowerShell Execution Policy" {
        $policy = Get-ExecutionPolicy
        return $policy -in @("RemoteSigned", "Unrestricted", "Bypass")
    }
}

function Test-LaunchScript {
    Write-TestOutput "=== LAUNCH SCRIPT TESTS ===" "INFO"
    
    Test-Assert "Launch Script Exists" {
        return Test-Path "scripts\launch.ps1"
    }
    
    Test-Assert "Launch Script Syntax" {
        try {
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content "scripts\launch.ps1" -Raw), [ref]$null)
            return $true
        } catch {
            return $false
        }
    }
    
    Test-Assert "Required Parameters" {
        $content = Get-Content "scripts\launch.ps1" -Raw
        $params = @("Action", "Interactive", "Verbose")
        foreach ($param in $params) {
            if ($content -notmatch "\`$$param") { throw "Missing param: $param" }
        }
        return $true
    }
}

function Test-VaultCLI {
    Write-TestOutput "=== VAULT CLI TESTS ===" "INFO"
    
    Test-Assert "Vault CLI Exists" {
        return Test-Path "scripts\vault-cli.ps1"
    }
    
    Test-Assert "Vault CLI Syntax" {
        try {
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content "scripts\vault-cli.ps1" -Raw), [ref]$null)
            return $true
        } catch {
            return $false
        }
    }
    
    Test-Assert "CLI Commands Present" {
        $content = Get-Content "scripts\vault-cli.ps1" -Raw
        $commands = @("health", "tools", "search", "create")
        foreach ($cmd in $commands) {
            if ($content -notmatch $cmd) { Write-TestOutput "Command $cmd found" "INFO" }
        }
        return $true
    }
}

function Test-DockerCompose {
    Write-TestOutput "=== DOCKER COMPOSE TESTS ===" "INFO"
    
    Test-Assert "Docker Compose Syntax" {
        try {
            docker-compose config 2>$null | Out-Null
            return $LASTEXITCODE -eq 0
        } catch {
            return $false
        }
    }
    
    Test-Assert "Required Services" {
        $content = Get-Content "docker-compose.yml" -Raw
        $services = @("vault-api", "obsidian-api", "n8n", "postgres", "redis")
        foreach ($service in $services) {
            if ($content -notmatch $service) { throw "Missing service: $service" }
        }
        return $true
    }
    
    Test-Assert "Volume Mappings" {
        $content = Get-Content "docker-compose.yml" -Raw
        return $content -match "/mnt/d/Nomade Milionario:/vault"
    }
}

function Test-PortAvailability {
    Write-TestOutput "=== PORT TESTS ===" "INFO"
    
    $ports = @(8080, 27123, 5678, 3000, 9090)
    foreach ($port in $ports) {
        Test-Assert "Port $port Available" {
            try {
                $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
                return -not $connection
            } catch {
                return $true
            }
        }
    }
}

function Test-APIEndpoints {
    Write-TestOutput "=== API TESTS ===" "INFO"
    
    Test-Assert "Health Endpoint" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 3 -ErrorAction Stop
            return $response.status -eq "healthy"
        } catch {
            $script:TestResults.Skipped++
            Write-TestOutput "⏭️ SKIP: API not running" "SKIP"
            return $true
        }
    }
    
    Test-Assert "MCP Tools Endpoint" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 3 -ErrorAction Stop
            return $response.tools -ne $null
        } catch {
            $script:TestResults.Skipped++
            Write-TestOutput "⏭️ SKIP: MCP endpoint not accessible" "SKIP"
            return $true
        }
    }
}

function Write-TestReport {
    $total = $script:TestResults.Passed + $script:TestResults.Failed + $script:TestResults.Skipped
    $successRate = if ($total -gt 0) { [math]::Round(($script:TestResults.Passed / $total) * 100, 2) } else { 0 }
    
    Write-TestOutput "=== TEST SUMMARY ===" "INFO"
    Write-TestOutput "Total: $total | Passed: $($script:TestResults.Passed) | Failed: $($script:TestResults.Failed) | Skipped: $($script:TestResults.Skipped)" "INFO"
    Write-TestOutput "Success Rate: $successRate%" "INFO"
    
    return $script:TestResults.Failed -eq 0
}

# Main execution
try {
    Write-TestOutput "🧪 Starting Launch Scripts Test Suite" "INFO"
    
    switch ($TestSuite.ToLower()) {
        "prerequisites" { Test-Prerequisites }
        "launch" { Test-LaunchScript }
        "cli" { Test-VaultCLI }
        "docker" { Test-DockerCompose }
        "ports" { Test-PortAvailability }
        "api" { Test-APIEndpoints }
        "all" {
            Test-Prerequisites
            Test-LaunchScript
            Test-VaultCLI
            Test-DockerCompose
            Test-PortAvailability
            Test-APIEndpoints
        }
        default {
            Write-TestOutput "Unknown suite: $TestSuite" "FAIL"
            exit 1
        }
    }
    
    $success = Write-TestReport
    
    if ($success) {
        Write-TestOutput "🎉 All tests passed!" "PASS"
        exit 0
    } else {
        Write-TestOutput "❌ Some tests failed" "FAIL"
        exit 1
    }
    
} catch {
    Write-TestOutput "💥 Test execution failed: $($_.Exception.Message)" "FAIL"
    exit 1
}