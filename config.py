"""
Pirate Radio AI - Configuration
"""
import os
import sys
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# FFmpeg (path to bin folder with ffmpeg.exe / ffprobe.exe)
FFMPEG_BIN_DIR = os.getenv("FFMPEG_BIN_DIR", "").strip().replace("/", os.sep)
if FFMPEG_BIN_DIR:
    _ff = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    _fp = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"
    FFMPEG_CMD = os.path.join(FFMPEG_BIN_DIR, _ff)
    FFPROBE_CMD = os.path.join(FFMPEG_BIN_DIR, _fp)
else:
    FFMPEG_CMD = "ffmpeg"
    FFPROBE_CMD = "ffprobe"

# Paths
BASE_DIR = Path(__file__).parent
MUSIC_DIR = BASE_DIR / "music"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"

# Create directories
for d in [MUSIC_DIR, OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(exist_ok=True)

# Radio Settings
RADIO_NAME = "Pirate AI Radio 🏴‍☠️"
RADIO_DESCRIPTION = "24/7 AI-generisane vijesti i muzika"
RADIO_GENRE = "News/Talk"

# Language & Voice
LANGUAGE = os.getenv("RADIO_LANGUAGE", "sr-RS")  # sr-RS, en-US, hr-HR, etc.
VOICE_NEWS = os.getenv("VOICE_NEWS", "sr-RS-NicholasNeural")  # Main news voice
VOICE_WEATHER = os.getenv("VOICE_WEATHER", "sr-RS-SophieNeural")  # Weather voice
VOICE_JINGLE = os.getenv("VOICE_JINGLE", "en-US-GuyNeural")  # Jingles

# Available Serbian voices:
# sr-RS-NicholasNeural (Male)
# sr-RS-SophieNeural (Female)

# Timing (in seconds)
NEWS_INTERVAL = int(os.getenv("NEWS_INTERVAL", "900"))  # 15 minutes
WEATHER_INTERVAL = int(os.getenv("WEATHER_INTERVAL", "1800"))  # 30 minutes
MUSIC_TRACK_LENGTH = int(os.getenv("MUSIC_TRACK_LENGTH", "180"))  # 3 min songs

# Audio Settings
SAMPLE_RATE = 24000
CHANNELS = 1
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.3"))  # Background music during talk
CROSSFADE_DURATION = 2  # seconds

# AI Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
NEWS_STYLE = os.getenv("NEWS_STYLE", "professional")  # professional, casual, dramatic

# Scraper Settings
REDDIT_SUBREDDITS = [
    "worldnews",
    "technology", 
    "science",
    "serbia",  # Za lokalne vijesti
]
RSS_FEEDS = [
    "https://www.b92.net/info/rss/vesti.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]
MAX_NEWS_ITEMS = 5

# Stream Settings
ICECAST_HOST = os.getenv("ICECAST_HOST", "localhost")
ICECAST_PORT = int(os.getenv("ICECAST_PORT", "8000"))
ICECAST_SOURCE_PASSWORD = os.getenv("ICECAST_PASSWORD", "hackme")
ICECAST_MOUNT = os.getenv("ICECAST_MOUNT", "/stream")
STREAM_BITRATE = 128  # kbps

# Weather API (free tier)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "Belgrade,RS")

# Prompts
NEWS_SYSTEM_PROMPT = """Ti si profesionalni radio voditelj na Pirate AI Radio. 
Tvoj zadatak je da čitaš vijesti na srpskom jeziku.
Stil: {style}
Pravila:
- Budi koncizan i jasan
- Koristi prirodan govorni jezik
- Dodaj kratke prelaze između vijesti
- Ne koristi emoji ili specijalne znakove
- Maksimalno 2-3 rečenice po vijesti"""

WEATHER_PROMPT = """Napravi kratku vremensku prognozu za radio.
Grad: {city}
Temperatura: {temp}°C
Opis: {description}
Vlažnost: {humidity}%
Vjetar: {wind} km/h

Stil: prirodan, prijateljski, kratak (2-3 rečenice)"""

JINGLE_TEXTS = [
    "Pirate AI Radio. Muzika. Vijesti. Dvadeset četiri sata.",
    "Slušate Pirate AI Radio. Vaš izvor informacija.",
    "Pirate Radio. Gdje AI sreće muziku.",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
