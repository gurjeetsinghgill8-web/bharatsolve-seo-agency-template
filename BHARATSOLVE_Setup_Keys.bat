@echo off
title BHARATSOLVE 🔐 Secure API Key Setup
color 0A
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       🚀 BHARATSOLVE SEO AGENCY                  ║
echo  ║       🔐 Secure API Key Setup                    ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  Your API keys will be encrypted with your PC's unique fingerprint.
echo  Even if someone steals this folder, they CANNOT read your keys.
echo.
echo  📌 Get FREE API keys from:
echo     Groq   → https://console.groq.com  (fast, free)
echo     Gemini → https://aistudio.google.com  (free tier)
echo.
echo  PRESS ANY KEY to start setup...
pause >nul
cls

:: Find Python automatically
set PYTHON_CMD=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo.
        echo  ❌ Python not found! Download from: https://python.org
        pause
        exit /b
    )
)

%PYTHON_CMD% secure_vault.py

if %errorlevel% neq 0 (
    echo.
    echo  ❌ Error running setup.
    pause
    exit /b
)

echo.
echo  ✅ Setup complete!
echo.
echo  📌 Now you can run the app using:
echo     Double-click "BHARATSOLVE_Launcher.bat"
echo.
pause
