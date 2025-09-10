# PowerShell script to run individual component tests
Write-Host "🚀 Starting Individual Component Testing" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Test ReRanker
Write-Host "`n🧪 Testing ReRanker Component..." -ForegroundColor Cyan
try {
    python test_reranker_individual.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ReRanker test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ ReRanker test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ ReRanker test ERROR: $_" -ForegroundColor Red
}

# Test TopicDetector
Write-Host "`n🧪 Testing TopicDetector Component..." -ForegroundColor Cyan
try {
    python test_topic_detector_individual.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ TopicDetector test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ TopicDetector test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ TopicDetector test ERROR: $_" -ForegroundColor Red
}

# Test SmartDocumentFilter
Write-Host "`n🧪 Testing SmartDocumentFilter Component..." -ForegroundColor Cyan
try {
    python simple_filter_test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SmartDocumentFilter test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ SmartDocumentFilter test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ SmartDocumentFilter test ERROR: $_" -ForegroundColor Red
}

# Test AdvancedContentProcessor
Write-Host "`n🧪 Testing AdvancedContentProcessor Component..." -ForegroundColor Cyan
try {
    python simple_processor_test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AdvancedContentProcessor test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ AdvancedContentProcessor test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ AdvancedContentProcessor test ERROR: $_" -ForegroundColor Red
}

# Test Validation Scripts
Write-Host "`n🧪 Testing Validation Scripts..." -ForegroundColor Cyan
try {
    python simple_validation_test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Validation scripts test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Validation scripts test FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Validation scripts test ERROR: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Individual Component Testing Completed!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow
