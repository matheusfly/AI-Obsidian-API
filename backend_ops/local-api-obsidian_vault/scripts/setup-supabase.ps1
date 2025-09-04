#!/usr/bin/env pwsh
# Supabase Integration Setup Script

Write-Host "🚀 Setting up Supabase Integration for AI Agent Retrieval..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create it first." -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing Supabase dependencies..." -ForegroundColor Yellow
Set-Location servicesservices/vault-api"
pip install supabase==2.3.4 postgrest==0.13.2
Set-Location ".."

# Test Supabase connection
Write-Host "🔗 Testing Supabase connection..." -ForegroundColor Yellow
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print('❌ SUPABASE_URL or SUPABASE_KEY not set in .env')
        exit(1)
    
    client = create_client(url, key)
    print('✅ Supabase connection successful!')
    print(f'📍 Connected to: {url}')
    
except Exception as e:
    print(f'❌ Supabase connection failed: {e}')
    exit(1)
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Supabase integration setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run the SQL schema in your Supabase dashboard: supabase-schema.sql" -ForegroundColor White
    Write-Host "2. Update SUPABASE_SERVICE_KEY in .env with your service role key" -ForegroundColor White
    Write-Host "3. Test the new endpoints:" -ForegroundColor White
    Write-Host "   - POST /api/v1/ai/retrieve" -ForegroundColor Gray
    Write-Host "   - POST /api/v1/agents/context" -ForegroundColor Gray
    Write-Host "   - GET /api/v1/supabase/health" -ForegroundColor Gray
} else {
    Write-Host "❌ Setup failed. Please check your configuration." -ForegroundColor Red
}