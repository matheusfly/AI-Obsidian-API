Write-Host "SYSTEM STATUS CHECK" -ForegroundColor Cyan

Write-Host "Jobs:" -ForegroundColor Yellow
Get-Job

Write-Host "Ports:" -ForegroundColor Yellow
$ports = @(8080, 27123, 3001, 3002)
foreach ($port in $ports) {
    $test = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($test) {
        Write-Host "Port $port OPEN" -ForegroundColor Green
    } else {
        Write-Host "Port $port CLOSED" -ForegroundColor Red
    }
}

Write-Host "API Tests:" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 3 | Out-Null
    Write-Host "Vault API OK" -ForegroundColor Green
} catch {
    Write-Host "Vault API FAIL" -ForegroundColor Red
}

try {
    Invoke-RestMethod -Uri "http://localhost:27123/health" -TimeoutSec 3 | Out-Null
    Write-Host "Obsidian API OK" -ForegroundColor Green
} catch {
    Write-Host "Obsidian API FAIL" -ForegroundColor Red
}

Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "http://localhost:8080/docs" -ForegroundColor White
Write-Host "http://localhost:27123" -ForegroundColor White
Write-Host "http://localhost:3001" -ForegroundColor White
Write-Host "http://localhost:3002" -ForegroundColor White