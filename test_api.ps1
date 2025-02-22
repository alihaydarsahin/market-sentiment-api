# Test API endpoints in PowerShell
Write-Host "Testing API..." -ForegroundColor Green

# 1. Test health endpoint
Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
    Write-Host "Health Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
}

# 2. Test login
Write-Host "`nTesting login..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $login.access_token
    Write-Host "Login successful! Token received." -ForegroundColor Green
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
    exit
}

# 3. Test prediction endpoint
Write-Host "`nTesting prediction endpoint..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$predictionBody = @{
    "reddit_sentiment" = 0.5
    "news_sentiment" = 0.3
    "market_change" = 0.1
} | ConvertTo-Json

try {
    $prediction = Invoke-RestMethod -Uri "http://localhost:5000/api/predict" `
        -Method Get `
        -Headers $headers `
        -Body $predictionBody
    
    Write-Host "Prediction result: $($prediction.prediction)" -ForegroundColor Green
} catch {
    Write-Host "Prediction failed: $_" -ForegroundColor Red
} 