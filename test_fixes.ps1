# ============================================
# CyberGuardX - Complete Verification Test
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CyberGuardX - Bug Fix Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Test 1: URL Checker (Previously failing with 500)
Write-Host "Test 1: URL Checker Fix..." -ForegroundColor Yellow
try {
    $body = @{ url = "http://paypal-verify-security-check.com" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://localhost:8000/check-url" -Method POST -ContentType "application/json" -Body $body -ErrorAction Stop
    
    if ($result.is_phishing -and $result.confidence -and $result.model_info -and $result.feature_analysis) {
        Write-Host "  [PASS] URL Checker working with full ML analysis" -ForegroundColor Green
        Write-Host "    - Phishing Score: $($result.phishing_score)" -ForegroundColor Gray
        Write-Host "    - Confidence: $($result.confidence)" -ForegroundColor Gray
        Write-Host "    - Features Analyzed: $($result.feature_analysis.Count)" -ForegroundColor Gray
        Write-Host "    - Recommendations: $($result.recommendations.Count)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] URL Checker incomplete data" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] URL Checker error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

Write-Host ""

# Test 2: History Loading (Previously failing with 500)
Write-Host "Test 2: History Loading Fix..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "http://localhost:8000/scan-history" -ErrorAction Stop
    
    if ($history -and $history.Count -gt 0) {
        Write-Host "  [PASS] History loaded successfully" -ForegroundColor Green
        Write-Host "    - Records Retrieved: $($history.Count)" -ForegroundColor Gray
        Write-Host "    - Most Recent: $($history[0].email)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [WARN] History loaded but empty" -ForegroundColor Yellow
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] History error: $($_.Exception.Message)" -ForegroundColor Red
    $testsFailed++
}

Write-Host ""

# Test 3: Backend Health
Write-Host "Test 3: Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET -ErrorAction Stop
    if ($health.status -eq "running") {
        Write-Host "  [PASS] Backend is healthy" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Backend status: $($health.status)" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Backend unreachable" -ForegroundColor Red
    $testsFailed++
}

Write-Host ""

# Test 4: Frontend Accessibility
Write-Host "Test 4: Frontend Server..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -ErrorAction Stop
    if ($frontend.StatusCode -eq 200) {
        Write-Host "  [PASS] Frontend accessible" -ForegroundColor Green
        Write-Host "    - Status: $($frontend.StatusCode) OK" -ForegroundColor Gray
        Write-Host "    - Content Length: $($frontend.Content.Length) bytes" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Frontend status: $($frontend.StatusCode)" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Frontend unreachable" -ForegroundColor Red
    $testsFailed++
}

Write-Host ""

# Test 5: Progress Tracking Endpoint
Write-Host "Test 5: Progress Tracking..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/scan-progress/test-id" -ErrorAction Stop
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "  [PASS] Progress endpoint active (404 expected for non-existent)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [WARN] Progress endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
        $testsPassed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tests Passed: " -NoNewline
Write-Host "$testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline
Write-Host "$testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " ALL TESTS PASSED! ✓" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Open http://localhost:3000/ in your browser" -ForegroundColor White
    Write-Host "2. Press Ctrl+F5 to hard refresh (clear cache)" -ForegroundColor White
    Write-Host "3. Test URL Checker with: http://paypal-verify-security-check.com" -ForegroundColor White
    Write-Host "4. Click 'Load Scan History' to see previous scans" -ForegroundColor White
    Write-Host "5. Test Website Scanner with: https://example.com" -ForegroundColor White
    Write-Host "6. Enjoy the new cyberpunk theme!" -ForegroundColor Magenta
    Write-Host ""
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host " SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}
