# 🔄 Flyde Flow Execution Script (PowerShell)
# Execute any Flyde flow with input data and output capture

param(
    [string]$FlowFile = "flows/hello-world.flyde",
    [string]$InputData = '{"message": "Hello from PowerShell script!"}',
    [string]$OutputFile = "output.json"
)

Write-Host "🔄 Executing Flow: $FlowFile" -ForegroundColor Green
Write-Host "📥 Input: $InputData" -ForegroundColor Blue
Write-Host "📤 Output: $OutputFile" -ForegroundColor Blue

# Run flow with input and save output
npx flyde run $FlowFile --input $InputData --output $OutputFile

Write-Host "✅ Flow execution complete!" -ForegroundColor Green
Write-Host "📄 Results saved to: $OutputFile" -ForegroundColor Cyan
