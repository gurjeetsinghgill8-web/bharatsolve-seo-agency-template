@echo off
title BHARATSOLVE 🚀 SEO Agency App
color 0B
cd /d "%~dp0"

:MENU
cls
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       🚀 BHARATSOLVE SEO AGENCY                  ║
echo  ║       Single Person AI SEO Agency                ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  [1] ▶  Start App (opens in browser)
echo  [2] 🔐 Setup/Change API Keys
echo  [3] 🗑️  Reset All Data
echo  [4] ❌ Exit
echo.
set /p choice="Select option (1-4): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto KEYS
if "%choice%"=="3" goto RESET
if "%choice%"=="4" goto EXIT
goto MENU

:KEYS
start "" "BHARATSOLVE_Setup_Keys.bat"
goto MENU

:RESET
cls
echo.
echo  ⚠️  ARE YOU SURE?
echo  This will delete:
echo    - All clients, projects, keywords, content
echo    - Encrypted API keys
echo    - Database and vault files
echo.
set /p confirm="Type YES to confirm: "
if /i "%confirm%"=="YES" (
    if exist seo_agency.db del /f /q seo_agency.db
    if exist .vault.enc del /f /q .vault.enc
    if exist .vault.salt del /f /q .vault.salt
    if exist .env del /f /q .env
    echo.
    echo  ✅ All data deleted. App will create fresh database on next start.
) else (
    echo.
    echo  ❌ Cancelled.
)
pause
goto MENU

:START
cls
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       🚀 Starting BHARATSOLVE...                 ║
echo  ║                                                  ║
echo  ║  Your browser will open automatically            ║
echo  ║  Default URL: http://localhost:8501              ║
echo  ║                                                  ║
echo  ║  Press Ctrl+C in this window to STOP the app     ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: Find Python automatically (supports Microsoft Store Python too)
set PYTHON_CMD=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo  ❌ Python not found! Download from: https://python.org
        pause
        goto MENU
    )
)

:: Check if streamlit is installed
%PYTHON_CMD% -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    echo  📥 Streamlit not found! Installing...
    %PYTHON_CMD% -m pip install streamlit
    echo.
)

:: Launch the app - browser opens automatically
%PYTHON_CMD% -m streamlit run app.py --server.headless=false --browser.gatherUsageStats=false

:: If app closes, pause so user can see errors
echo.
echo  ⚠️  App has stopped.
pause
goto MENU

:EXIT
cls
echo.
echo  🤖 Thanks for using BHARATSOLVE SEO AGENCY!
echo  Made with ❤️ in India
echo.
timeout /t 2 >nul
exit
