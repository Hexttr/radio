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
RADIO_DESCRIPTION = "24/7 музыка и новости"
RADIO_GENRE = "News/Talk"

# Language & Voice (по умолчанию — только русский)
LANGUAGE = os.getenv("RADIO_LANGUAGE", "ru-RU")
VOICE_NEWS = os.getenv("VOICE_NEWS", "ru-RU-DmitryNeural")
VOICE_WEATHER = os.getenv("VOICE_WEATHER", "ru-RU-SvetlanaNeural")
VOICE_JINGLE = os.getenv("VOICE_JINGLE", "ru-RU-DmitryNeural")

# Как часто вставки (в секундах)
NEWS_INTERVAL = int(os.getenv("NEWS_INTERVAL", "900"))      # новости: каждые 15 мин
WEATHER_INTERVAL = int(os.getenv("WEATHER_INTERVAL", "1800"))  # погода: каждые 30 мин
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

# Weather (wttr.in, без ключа)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "Moscow,RU")

# Prompts by language (lang code: ru, en, sr)
NEWS_SYSTEM_PROMPTS = {
    "ru": """Ты ведущий радио на Pirate AI Radio. Читай новости на русском языке.
Стиль: {style}
Правила:
- Кратко и ясно
- Разговорный язык
- Короткие переходы между новостями
- Без эмодзи и спецсимволов
- 2-3 предложения на новость""",
    "en": """You are a radio host on Pirate AI Radio. Read the news in English.
Style: {style}
Rules:
- Be concise and clear
- Use natural spoken language
- Short transitions between stories
- No emoji or special characters
- 2-3 sentences per story""",
    "sr": """Ti si profesionalni radio voditelj na Pirate AI Radio. 
Čitaš vijesti na srpskom jeziku.
Stil: {style}
Pravila:
- Budi koncizan i jasan
- Prirodan govorni jezik
- Kratki prelazi između vijesti
- Bez emoji
- 2-3 rečenice po vijesti""",
}
WEATHER_PROMPTS = {
    "ru": """Сделай короткий прогноз погоды для радио.
Город: {city}
Температура: {temp}°C
Описание: {description}
Влажность: {humidity}%
Ветер: {wind} км/ч
Стиль: дружелюбно, коротко (2-3 предложения)""",
    "en": """Write a short weather forecast for radio.
City: {city}
Temperature: {temp}°C
Description: {description}
Humidity: {humidity}%
Wind: {wind} km/h
Style: friendly, short (2-3 sentences)""",
    "sr": """Napravi kratku vremensku prognozu za radio.
Grad: {city}
Temperatura: {temp}°C
Opis: {description}
Vlažnost: {humidity}%
Vjetar: {wind} km/h
Stil: prirodan, kratak (2-3 rečenice)""",
}
# Backward compatibility
NEWS_SYSTEM_PROMPT = NEWS_SYSTEM_PROMPTS.get("sr", list(NEWS_SYSTEM_PROMPTS.values())[0])
WEATHER_PROMPT = WEATHER_PROMPTS.get("sr", list(WEATHER_PROMPTS.values())[0])

JINGLE_TEXTS_BY_LANG = {
    "ru": [
        "Pirate AI Radio. Музыка. Новости. Круглые сутки.",
        "Вы слушаете Pirate AI Radio. Ваш источник информации.",
        "Pirate Radio. Где ИИ встречается с музыкой.",
    ],
    "en": [
        "Pirate AI Radio. Music. News. Twenty-four seven.",
        "You're listening to Pirate AI Radio. Your source of information.",
        "Pirate Radio. Where AI meets music.",
    ],
    "sr": [
        "Pirate AI Radio. Muzika. Vijesti. Dvadeset četiri sata.",
        "Slušate Pirate AI Radio. Vaš izvor informacija.",
        "Pirate Radio. Gdje AI sreće muziku.",
    ],
}
# News prompt instructions (language for AI output)
NEWS_PROMPT_LANG = {
    "ru": """ПРАВИЛА:
- Пиши на русском языке
- Каждая новость 2-3 предложения
- Переходы: "А теперь...", "В других новостях..."
- Начни с приветствия, закончи "Это были новости, возвращаемся к музыке"
- Не более 300 слов, без эмодзи""",
    "en": """RULES:
- Write in English
- 2-3 sentences per story
- Transitions: "And now...", "In other news..."
- Start with a greeting, end with "That was the news, back to music"
- No more than 300 words, no emoji""",
    "sr": """PRAVILA:
- Piši na srpskom jeziku
- Svaka vijest 2-3 rečenice
- Prelazi: "A sada...", "U drugim vijestima..."
- Počni pozdravom, završi "To su bile vijesti, vraćamo se muzici"
- Ne više od 300 riječi, bez emoji""",
}
# Lang code from RADIO_LANGUAGE (ru-RU -> ru, en-US -> en)
def _prompt_lang():
    raw = (os.getenv("RADIO_LANGUAGE") or LANGUAGE).strip()
    return raw.split("-")[0].lower() if raw else "ru"

PROMPT_LANG = _prompt_lang()
JINGLE_TEXTS = JINGLE_TEXTS_BY_LANG.get(PROMPT_LANG, JINGLE_TEXTS_BY_LANG["en"])
# Jingle before news block (short phrase)
JINGLE_NEWS_PHRASE = {"ru": "Новости на Pirate Radio.", "en": "News on Pirate Radio.", "sr": "Vijesti na Pirate Radiju."}
JINGLE_NEWS = JINGLE_NEWS_PHRASE.get(PROMPT_LANG, JINGLE_NEWS_PHRASE["en"])

# Filler / intro / outro by language (for AI writer)
FILLER_TEXTS = {
    "ru": [
        "Пока нет свежих новостей. Продолжайте слушать музыку на Pirate Radio.",
        "Новости готовятся. А пока — музыка.",
        "Спасибо, что слушаете Pirate Radio. Новости скоро.",
    ],
    "en": [
        "No news updates at the moment. Enjoy the music on Pirate Radio.",
        "News is being prepared. In the meantime, enjoy the music.",
        "Thanks for listening to Pirate Radio. News coming up soon.",
    ],
    "sr": [
        "Trenutno nemamo novih vijesti. Nastavite da uživate u muzici na Pirate Radiju.",
        "Vijesti se pripremaju. U međuvremenu, uživajte u muzici.",
        "Hvala što slušate Pirate Radio. Vijesti stižu uskoro.",
    ],
}
INTRO_TEXTS = {
    "ru": [
        "Добро пожаловать на Pirate AI Radio! Музыка и новости круглые сутки.",
        "Это Pirate Radio. Автоматически. Без остановки.",
        "Pirate AI Radio в эфире! Оставайтесь с нами.",
        "Вы слушаете Pirate Radio — где технологии встречаются с музыкой.",
    ],
    "en": [
        "Welcome to Pirate AI Radio! Your source of music and news, twenty-four seven.",
        "This is Pirate Radio. Automated. Infinite. Just for you.",
        "Pirate AI Radio on the air! Stay with us.",
        "You're listening to Pirate Radio, where tech meets music.",
    ],
    "sr": [
        "Dobrodošli na Pirate AI Radio! Vaš izvor muzike i informacija, dvadeset četiri sata.",
        "Ovo je Pirate Radio. Automatizovano. Beskonačno. Samo za vas.",
        "Pirate AI Radio na talasima! Ostanite s nama.",
        "Slušate Pirate Radio, gdje tehnologija sreće muziku.",
    ],
}
OUTRO_TEXTS = {
    "ru": [
        "Это были новости. Продолжайте слушать.",
        "Спасибо, что были с нами. Возвращаемся к музыке.",
        "Pirate Radio продолжает программу.",
        "Оставайтесь на волне, после музыки вернёмся.",
    ],
    "en": [
        "That was the news. Keep listening.",
        "Thanks for being with us. Music is back.",
        "Pirate Radio continues the program.",
        "Stay tuned, we'll be back after the music.",
    ],
    "sr": [
        "To su bile vijesti. Nastavite da nas slušate.",
        "Hvala što ste bili s nama. Muzika se vraća.",
        "Pirate Radio nastavlja sa programom.",
        "Ostanite na vezi, vraćamo se nakon muzike.",
    ],
}
TIME_TEMPLATES = {
    "ru": ["Сейчас {time}.", "Время {time}. Вы слушаете Pirate Radio.", "На Pirate Radio сейчас {time}."],
    "en": ["The time is {time}.", "It's {time}. You're listening to Pirate Radio.", "On Pirate Radio it's {time}."],
    "sr": ["Tačno je {time}.", "Vrijeme je {time}. Slušate Pirate Radio.", "Na Pirate Radiju je {time}."],
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
