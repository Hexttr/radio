@echo off
cd /d "%~dp0"
echo Starting Pirate Radio AI...
echo Add your MP3/WAV/OGG/FLAC files to the "music" folder.
echo Optional: GROQ_API_KEY in .env for AI news (free at console.groq.com)
echo Optional: FFmpeg in PATH for music mixing (ffmpeg.org)
echo.
python -m src.radio
pause
