# Test Semantic Search Tool
Write-Host "Testing Semantic Search Tool..." -ForegroundColor Yellow

$payload = @{
    tool = "semantic_search"
    params = @{
        query = "test query"
        top_k = 3
    }
} | ConvertTo-Json

Write-Host "Payload: $payload" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3011/tools/execute" -Method POST -Body $payload -ContentType "application/json"
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 10)" -ForegroundColor White
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}
