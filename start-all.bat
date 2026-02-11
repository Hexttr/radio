@echo off
cd /d "%~dp0"
set "NGROK_BIN=C:\Users\User\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe"
if exist "%~dp0ngrok.yml" (set "NGROK_CONFIG=%~dp0ngrok.yml") else (set "NGROK_CONFIG=%LOCALAPPDATA%\ngrok\ngrok.yml")
if not exist "%NGROK_CONFIG%" (
    echo [ERROR] ngrok config not found: %NGROK_CONFIG%
    pause
    exit /b 1
)
if not exist "%NGROK_BIN%" (
    echo [ERROR] ngrok.exe not found: %NGROK_BIN%
    pause
    exit /b 1
)
if not defined FFMPEG_BIN_DIR set "FFMPEG_BIN_DIR=C:\Users\User\Downloads\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\bin"
if exist "%FFMPEG_BIN_DIR%\ffmpeg.exe" set "PATH=%FFMPEG_BIN_DIR%;%PATH%"
echo Starting Лучшее ИИ Радио + ngrok...
echo.
echo [1/2] Starting radio in new window...
start "Radio" cmd /k "cd /d "%~dp0" && set PATH=%PATH% && python -m src.radio"
echo [2/2] Waiting for radio to start...
timeout /t 8 /nobreak >nul
echo.
echo Starting ngrok tunnel. Share the URL from the output below:
echo.
"%NGROK_BIN%" http 9090 --config="%NGROK_CONFIG%"
pause
