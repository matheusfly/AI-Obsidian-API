# 🔄 Motia Step Execution Script (PowerShell)
# Execute any Motia step with input data and output capture

param(
    [string]$StepFile = "steps/hello-world.step.ts",
    [string]$InputData = '{"message": "Hello from PowerShell script!"}',
    [string]$OutputFile = "output.json"
)

Write-Host "🔄 Executing Step: $StepFile" -ForegroundColor Green
Write-Host "📥 Input: $InputData" -ForegroundColor Blue
Write-Host "📤 Output: $OutputFile" -ForegroundColor Blue

# Run step with input and save output
npx motia run $StepFile --input $InputData --output $OutputFile

Write-Host "✅ Step execution complete!" -ForegroundColor Green
Write-Host "📄 Results saved to: $OutputFile" -ForegroundColor Cyan
