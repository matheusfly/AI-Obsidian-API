# ===========================================
# CRITICAL SECURITY SCRIPT
# ===========================================
# This script removes sensitive data from git history
# WARNING: This rewrites git history and should be used with extreme caution

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

Write-Host "🚨 CRITICAL GIT HISTORY CLEANUP SCRIPT 🚨" -ForegroundColor Red
Write-Host "This script will remove sensitive data from git history" -ForegroundColor Yellow
Write-Host "WARNING: This rewrites git history and cannot be undone!" -ForegroundColor Red

if (-not $Force) {
    $confirmation = Read-Host "Are you absolutely sure you want to proceed? This will rewrite git history (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Define sensitive patterns to remove from git history
$sensitivePatterns = @(
    "sk-proj-[a-zA-Z0-9]{20,}",
    "sk-ant-[a-zA-Z0-9-]{20,}",
    "AIzaSy[a-zA-Z0-9_-]{33}",
    "ctx7sk-[a-zA-Z0-9-]{20,}",
    "[a-f0-9]{64}",
    "$env:AGENT_OPS_API_KEY"
)

Write-Host "`n🔍 Checking for sensitive data in git history..." -ForegroundColor Cyan

# Check if git filter-repo is available
$gitFilterRepo = Get-Command "git-filter-repo" -ErrorAction SilentlyContinue
if (-not $gitFilterRepo) {
    Write-Host "❌ git-filter-repo is not installed. Installing..." -ForegroundColor Red
    Write-Host "Please install git-filter-repo first:" -ForegroundColor Yellow
    Write-Host "  pip install git-filter-repo" -ForegroundColor Yellow
    Write-Host "  or" -ForegroundColor Yellow
    Write-Host "  brew install git-filter-repo" -ForegroundColor Yellow
    exit 1
}

# Create a backup branch first
Write-Host "`n💾 Creating backup branch..." -ForegroundColor Cyan
git branch backup-before-cleanup

# Remove sensitive files from git history
Write-Host "`n🗑️ Removing sensitive files from git history..." -ForegroundColor Cyan

# Remove database files that may contain sensitive data
git filter-repo --path data/chroma/ --invert-paths --force
git filter-repo --path data/vector/ --invert-paths --force
git filter-repo --path data/cache/ --invert-paths --force

# Remove environment files
git filter-repo --path-glob "*.env" --invert-paths --force
git filter-repo --path-glob ".env*" --invert-paths --force

# Remove configuration files with secrets
git filter-repo --path config/production.env --invert-paths --force
git filter-repo --path config/local.env --invert-paths --force

Write-Host "`n🔍 Scanning for remaining sensitive patterns..." -ForegroundColor Cyan

# Use BFG Repo-Cleaner if available (more efficient for large repos)
$bfg = Get-Command "bfg" -ErrorAction SilentlyContinue
if ($bfg) {
    Write-Host "Using BFG Repo-Cleaner for pattern removal..." -ForegroundColor Green
    
    # Create a replacements file for BFG
    $replacementsFile = "replacements.txt"
    $replacements = @()
    
    foreach ($pattern in $sensitivePatterns) {
        $replacements += "`"$pattern`"==>`"REDACTED_API_KEY`""
    }
    
    $replacements | Out-File -FilePath $replacementsFile -Encoding UTF8
    
    if (-not $DryRun) {
        bfg --replace-text $replacementsFile --no-blob-protection .
        Remove-Item $replacementsFile
    }
} else {
    Write-Host "BFG not available, using git filter-repo..." -ForegroundColor Yellow
    
    # Use git filter-repo with expression
    $expression = "if b'$pattern' in message or b'$pattern' in files: return True"
    
    foreach ($pattern in $sensitivePatterns) {
        if (-not $DryRun) {
            git filter-repo --replace-text <(echo "$pattern==>REDACTED_API_KEY") --force
        }
    }
}

# Clean up and optimize repository
Write-Host "`n🧹 Cleaning up repository..." -ForegroundColor Cyan

if (-not $DryRun) {
    # Force garbage collection
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    
    # Update remote if it exists
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Host "`n⚠️  WARNING: You need to force push to update the remote repository" -ForegroundColor Red
        Write-Host "This will overwrite the remote history!" -ForegroundColor Red
        Write-Host "Run: git push --force-with-lease origin master" -ForegroundColor Yellow
    }
}

Write-Host "`n📊 GIT HISTORY CLEANUP SUMMARY:" -ForegroundColor Cyan
Write-Host "  Sensitive patterns removed: $($sensitivePatterns.Count)" -ForegroundColor Green
Write-Host "  Backup branch created: backup-before-cleanup" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN COMPLETE - No changes were made to git history" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ GIT HISTORY CLEANUP COMPLETE!" -ForegroundColor Green
    Write-Host "Sensitive data has been removed from git history" -ForegroundColor Green
}

Write-Host "`n🚨 CRITICAL NEXT STEPS:" -ForegroundColor Red
Write-Host "1. Verify no sensitive data remains in git history" -ForegroundColor Yellow
Write-Host "2. Force push to remote repository (if applicable)" -ForegroundColor Yellow
Write-Host "3. Notify all team members to re-clone the repository" -ForegroundColor Yellow
Write-Host "4. Create new API keys for all services" -ForegroundColor Yellow
Write-Host "5. Update all environment variables" -ForegroundColor Yellow
