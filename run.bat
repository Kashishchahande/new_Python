@echo off
title Digital Notice Board Server
echo ==============================================
echo    Starting Digital Notice Board Server...
echo ==============================================
echo.
"C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe" app.py
if errorlevel 1 (
    python app.py
)
pause
