# ===========================================
# CRITICAL SECURITY SCRIPT
# ===========================================
# This script replaces all hardcoded API keys with environment variables
# Run this IMMEDIATELY after any security breach

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

Write-Host "🚨 CRITICAL SECURITY CLEANUP SCRIPT 🚨" -ForegroundColor Red
Write-Host "This script will replace all hardcoded API keys with environment variables" -ForegroundColor Yellow

if (-not $Force) {
    $confirmation = Read-Host "Are you sure you want to proceed? This will modify files across the entire codebase (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Define the API keys to replace
$apiKeys = @{
    "$env:OPENAI_API_KEY" = "`$env:OPENAI_API_KEY"
    "$env:GOOGLE_API_KEY" = "`$env:GOOGLE_API_KEY"
    "$env:ACI_KEY" = "`$env:ACI_KEY"
    "$env:CONTEXT7_API_KEY" = "`$env:CONTEXT7_API_KEY"
    "$env:AGENT_OPS_API_KEY" = "`$env:AGENT_OPS_API_KEY"
}

# Define file patterns to search
$filePatterns = @(
    "*.ps1",
    "*.py",
    "*.js",
    "*.json",
    "*.md",
    "*.txt",
    "*.yml",
    "*.yaml"
)

$totalFiles = 0
$modifiedFiles = 0
$errors = @()

Write-Host "`n🔍 Scanning for hardcoded API keys..." -ForegroundColor Cyan

foreach ($pattern in $filePatterns) {
    $files = Get-ChildItem -Path . -Recurse -Include $pattern -File | Where-Object { 
        $_.FullName -notmatch "\.git\\" -and 
        $_.FullName -notmatch "node_modules\\" -and
        $_.FullName -notmatch "venv\\" -and
        $_.FullName -notmatch "env\\" -and
        $_.FullName -notmatch "__pycache__\\" -and
        $_.FullName -notmatch "\.gitignore"
    }
    
    foreach ($file in $files) {
        $totalFiles++
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        
        if ($content) {
            $originalContent = $content
            $fileModified = $false
            
            foreach ($key in $apiKeys.Keys) {
                if ($content -match [regex]::Escape($key)) {
                    if ($DryRun) {
                        Write-Host "  [DRY RUN] Would replace key in: $($file.FullName)" -ForegroundColor Yellow
                    } else {
                        $content = $content -replace [regex]::Escape($key), $apiKeys[$key]
                        $fileModified = $true
                    }
                }
            }
            
            if ($fileModified -and -not $DryRun) {
                try {
                    Set-Content -Path $file.FullName -Value $content -NoNewline
                    Write-Host "  ✅ Updated: $($file.FullName)" -ForegroundColor Green
                    $modifiedFiles++
                } catch {
                    $errors += "Failed to update $($file.FullName): $($_.Exception.Message)"
                    Write-Host "  ❌ Error updating: $($file.FullName)" -ForegroundColor Red
                }
            }
        }
    }
}

Write-Host "`n📊 SECURITY CLEANUP SUMMARY:" -ForegroundColor Cyan
Write-Host "  Total files scanned: $totalFiles" -ForegroundColor White
Write-Host "  Files modified: $modifiedFiles" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host "  Errors encountered: $($errors.Count)" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "    - $error" -ForegroundColor Red
    }
}

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN COMPLETE - No files were actually modified" -ForegroundColor Yellow
    Write-Host "Run with -Force to apply changes" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ API KEY SECURITY CLEANUP COMPLETE!" -ForegroundColor Green
    Write-Host "All hardcoded API keys have been replaced with environment variables" -ForegroundColor Green
}

Write-Host "`n🚨 CRITICAL NEXT STEPS:" -ForegroundColor Red
Write-Host "1. Create new API keys for all services" -ForegroundColor Yellow
Write-Host "2. Set environment variables in your system" -ForegroundColor Yellow
Write-Host "3. Remove sensitive data from git history" -ForegroundColor Yellow
Write-Host "4. Test all functionality with new environment variables" -ForegroundColor Yellow
Write-Host "5. Monitor for any remaining hardcoded keys" -ForegroundColor Yellow
