# CyberGuardX v2.0 - Complete Test Script
# Tests all endpoints: Email Breach, URL Phishing, Website Scanner

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  CYBERGUARDX v2.0 - ENDPOINT TESTS" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Test 1: Email Breach Detection
Write-Host "[1/4] Testing Email Breach Check..." -ForegroundColor Yellow
try {
    $email = Invoke-RestMethod -Uri "http://localhost:8000/check-email" -Method POST `
        -Body '{"email": "test@example.com"}' -ContentType "application/json"
    Write-Host "  ✓ Result: $($email.email)" -ForegroundColor Green
    Write-Host "    Breached: $($email.breached)" -ForegroundColor White
    Write-Host "    Risk Level: $($email.risk_level)" -ForegroundColor White
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: URL Phishing Detection
Write-Host "`n[2/4] Testing URL Phishing Detection..." -ForegroundColor Yellow
try {
    $url = Invoke-RestMethod -Uri "http://localhost:8000/check-url" -Method POST `
        -Body '{"url": "http://suspicious-paypal-login.net"}' -ContentType "application/json"
    Write-Host "  ✓ URL analyzed: $($url.url)" -ForegroundColor Green
    Write-Host "    Is Phishing: $($url.is_phishing)" -ForegroundColor White
    Write-Host "    Confidence: $($url.phishing_score)%" -ForegroundColor White
    Write-Host "    Risk Level: $($url.risk_level)" -ForegroundColor White
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Website Security Scanner
Write-Host "`n[3/4] Testing Website Security Scanner (example.com)..." -ForegroundColor Yellow
try {
    $scanBody = @{
        url = "https://example.com"
        confirmed_permission = $true
        owner_confirmation = $true
        legal_responsibility = $true
    } | ConvertTo-Json

    $scan = Invoke-RestMethod -Uri "http://localhost:8000/scan-website" -Method POST `
        -Body $scanBody -ContentType "application/json"
    
    Write-Host "  ✓ Scan completed in $($scan.scan_duration_ms)ms" -ForegroundColor Green
    Write-Host "    Overall Grade: $($scan.overall_grade) | Risk Score: $($scan.risk_score)/100" -ForegroundColor White
    Write-Host "    HTTP Headers: $($scan.http_grade) | SSL/TLS: $($scan.ssl_grade) | DNS: $($scan.dns_grade)" -ForegroundColor White
    Write-Host "    Critical Issues: $($scan.critical_issues_count) | High: $($scan.high_issues_count) | Medium: $($scan.medium_issues_count)" -ForegroundColor White
    Write-Host "`n    Top 3 Recommendations:" -ForegroundColor Cyan
    $scan.recommendations | Select-Object -First 3 | ForEach-Object {
        Write-Host "      • $_" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Scan History
Write-Host "`n[4/4] Testing Scan History..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "http://localhost:8000/scan-history" -Method GET
    Write-Host "  ✓ Total scans in database: $($history.Count)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "  STATUS: All CyberGuardX systems tested! ✓" -ForegroundColor Green
Write-Host "  Access API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "===========================================`n" -ForegroundColor Cyan
