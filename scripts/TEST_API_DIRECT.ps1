# Direct API Test
Write-Host "🔍 DIRECT API TEST" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green

$apiBaseURL = "https://127.0.0.1:27124"
$apiToken = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

try {
    Write-Host "🌐 Testing API: $apiBaseURL" -ForegroundColor Cyan
    
    $headers = @{
        'Authorization' = "Bearer $apiToken"
    }
    
    $response = Invoke-WebRequest -Uri "$apiBaseURL/vault/" -Headers $headers -SkipCertificateCheck -TimeoutSec 10
    
    Write-Host "✅ Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📥 Response Length: $($response.Content.Length) bytes" -ForegroundColor Green
    
    # Show first 500 characters
    Write-Host "📥 First 500 characters:" -ForegroundColor Yellow
    Write-Host $response.Content.Substring(0, [Math]::Min(500, $response.Content.Length)) -ForegroundColor White
    
    # Parse JSON
    $json = $response.Content | ConvertFrom-Json
    $files = $json.files
    
    Write-Host "📄 Files found: $($files.Count)" -ForegroundColor Green
    
    if ($files.Count -gt 0) {
        Write-Host "📄 First 10 files:" -ForegroundColor Cyan
        for ($i = 0; $i -lt [Math]::Min(10, $files.Count); $i++) {
            Write-Host "   $($i+1). $($files[$i])" -ForegroundColor White
        }
        
        # Test searches
        $queries = @("logica", "matematica", "performance", "test", "md", "API", "AGENTS")
        foreach ($query in $queries) {
            $matches = $files | Where-Object { $_.ToLower() -like "*$($query.ToLower())*" }
            Write-Host "🔍 Search '$query': $($matches.Count) matches" -ForegroundColor Yellow
            if ($matches.Count -gt 0 -and $matches.Count -le 5) {
                foreach ($match in $matches) {
                    Write-Host "   - $match" -ForegroundColor White
                }
            }
        }
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "❌ Full Error: $($_.Exception)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host
