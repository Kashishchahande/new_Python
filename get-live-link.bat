@echo off
title Digital Notice Board - Live Link
cls
echo ================================================================
echo       DIGITAL NOTICE BOARD - LIVE INTERNET LINK GENERATOR
echo ================================================================
echo.
echo [1/2] Checking local server...
start "Digital Notice Board Server" /min "C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe" app.py
timeout /t 2 /nobreak >nul

echo [2/2] Generating Live Public Link...
echo.
echo ================================================================
echo  Neeche jo "https://" link aayegi, use copy karke Mam ko bhej dein:
echo  (Jab tak Mam check kar rahi hain, is window ko khula rakhein)
echo ================================================================
echo.
ssh -o StrictHostKeyChecking=no -p 443 -R0:localhost:5000 a.pinggy.io
if errorlevel 1 (
    echo.
    echo Trying alternative secure tunnel...
    ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 nokey@localhost.run
)
pause
