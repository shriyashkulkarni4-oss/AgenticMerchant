# Start AgenticBuy FastAPI Backend
$env:PYTHONPATH = "$PSScriptRoot\backend"
Write-Host "Starting AgenticBuy Backend on http://localhost:8080..." -ForegroundColor Green
& "$PSScriptRoot\..\.hack\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --app-dir "$PSScriptRoot\backend"
