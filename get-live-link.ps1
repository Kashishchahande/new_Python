Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       DIGITAL NOTICE BOARD - LIVE INTERNET LINK GENERATOR" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Starting server in background..." -ForegroundColor Yellow
Start-Process -WindowStyle Minimized -FilePath "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -ArgumentList "app.py"
Start-Sleep -Seconds 2

Write-Host "[2/2] Generating Live Public Link..." -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Neeche jo 'https://' link aayegi, use copy karke Mam ko bhej dein:" -ForegroundColor White
Write-Host " (Jab tak Mam check kar rahi hain, is window ko khula rakhein)" -ForegroundColor DarkGray
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

ssh -o StrictHostKeyChecking=no -p 443 -R0:localhost:5000 a.pinggy.io
if ($LASTEXITCODE -ne 0) {
    ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 nokey@localhost.run
}
