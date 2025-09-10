Write-Host scripts/ING SYSTEM PATHS..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVer = python --version
    Write-Host "Python OK: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "Python MISSING - Install Python 3.11+" -ForegroundColor Red
}

# Check Node
try {
    $nodeVer = node --version
    Write-Host "Node OK: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "Node MISSING - Install Node.js 18+" -ForegroundColor Red
}

# Check npm
try {
    $npmVer = npm --version
    Write-Host "npm OK: $npmVer" -ForegroundColor Green
} catch {
    Write-Host "npm MISSING" -ForegroundColor Red
}

# Install dependencies
Write-Host scripts/ing Python deps..." -ForegroundColor Yellow
cd vault-api
pip install -r requirements.txt --quiet
cd ..

Write-Host scripts/ing Node deps..." -ForegroundColor Yellow
cd obsidian-api
npm install --silent
cd ..

cd motia-project
npm install --silent
cd ..

cd flyde-project
npm install --silent
cd ..

Write-Host "PATHS FIXED!" -ForegroundColor Green