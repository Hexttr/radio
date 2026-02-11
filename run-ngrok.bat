@echo off
cd /d "%~dp0"
set "NGROK_BIN=C:\Users\User\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe"
if exist "%~dp0ngrok.yml" (set "NGROK_CONFIG=%~dp0ngrok.yml") else (set "NGROK_CONFIG=%LOCALAPPDATA%\ngrok\ngrok.yml")
if not exist "%NGROK_CONFIG%" (
    echo [ERROR] ngrok config not found: %NGROK_CONFIG%
    echo Put ngrok.yml with authtoken in this folder or %LOCALAPPDATA%\ngrok\
    pause
    exit /b 1
)
if not exist "%NGROK_BIN%" (
    echo [ERROR] ngrok.exe not found: %NGROK_BIN%
    pause
    exit /b 1
)
echo Starting ngrok tunnel for port 9090...
echo Radio must be running (run.bat) before connecting.
echo.
"%NGROK_BIN%" http 9090 --config="%NGROK_CONFIG%"
pause
