@echo off
cd /d "%~dp0"
if not defined FFMPEG_BIN_DIR set "FFMPEG_BIN_DIR=C:\Users\User\Downloads\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\bin"
if exist "%FFMPEG_BIN_DIR%\ffmpeg.exe" set "PATH=%FFMPEG_BIN_DIR%;%PATH%"
echo Starting Pirate Radio AI...
echo Music: music\ folder. FFmpeg: %FFMPEG_BIN_DIR%
echo.
python -m src.radio
pause
