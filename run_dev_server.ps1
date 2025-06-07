# Run FastAPI server using Poetry and Uvicorn
Write-Host "Starting SpeakEase API server..." -ForegroundColor Green
$env:K_SERVICE = "true"
$env:GOOGLE_APPLICATION_CREDENTIALS = "gcpxmlb25-e063bdf91528.json"
poetry run uvicorn app.main:app --reload 