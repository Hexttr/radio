"""
Лучшее ИИ Радио - Configuration
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
RADIO_NAME = "Лучшее ИИ Радио"
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
    "https://lenta.ru/rss/news",
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
    "ru": """Ты ведущий радио на Лучшее ИИ Радио. Читай новости на русском языке.
Стиль: {style}
Правила:
- Кратко и ясно
- Разговорный язык
- Короткие переходы между новостями
- Без эмодзи и спецсимволов
- 2-3 предложения на новость""",
    "en": """You are a radio host on Лучшее ИИ Радио. Read the news in English.
Style: {style}
Rules:
- Be concise and clear
- Use natural spoken language
- Short transitions between stories
- No emoji or special characters
- 2-3 sentences per story""",
    "sr": """Ti si profesionalni radio voditelj na Лучшее ИИ Радио. 
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
        "Лучшее ИИ Радио. Музыка. Новости. Круглые сутки.",
        "Вы слушаете Лучшее ИИ Радио. Ваш источник информации.",
        "Лучшее ИИ Радио. Где ИИ встречается с музыкой.",
    ],
    "en": [
        "Лучшее ИИ Радио. Музыка. Новости. Круглые сутки.",
        "You're listening to Лучшее ИИ Радио. Your source of information.",
        "Лучшее ИИ Радио. Where AI meets music.",
    ],
    "sr": [
        "Лучшее ИИ Радио. Muzika. Vijesti. Dvadeset četiri sata.",
        "Slušate Лучшее ИИ Радио. Vaš izvor informacija.",
        "Лучшее ИИ Радио. Gdje AI sreće muziku.",
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
JINGLE_NEWS_PHRASE = {"ru": "Новости на Лучшее ИИ Радио.", "en": "News on Лучшее ИИ Радио.", "sr": "Vijesti na Лучшее ИИ Radiju."}
JINGLE_NEWS = JINGLE_NEWS_PHRASE.get(PROMPT_LANG, JINGLE_NEWS_PHRASE["en"])

# Filler / intro / outro by language (for AI writer)
FILLER_TEXTS = {
    "ru": [
        "Пока нет свежих новостей. Продолжайте слушать музыку на Лучшее ИИ Радио.",
        "Новости готовятся. А пока — музыка.",
        "Спасибо, что слушаете Лучшее ИИ Радио. Новости скоро.",
    ],
    "en": [
        "No news updates at the moment. Enjoy the music on Лучшее ИИ Радио.",
        "News is being prepared. In the meantime, enjoy the music.",
        "Thanks for listening to Лучшее ИИ Радио. News coming up soon.",
    ],
    "sr": [
        "Trenutno nemamo novih vijesti. Nastavite da uživate u muzici na Лучшее ИИ Radiju.",
        "Vijesti se pripremaju. U međuvremenu, uživajte u muzici.",
        "Hvala što slušate Лучшее ИИ Радио. Vijesti stižu uskoro.",
    ],
}
INTRO_TEXTS = {
    "ru": [
        "Добро пожаловать на Лучшее ИИ Радио! Музыка и новости круглые сутки.",
        "Это Лучшее ИИ Радио. Автоматически. Без остановки.",
        "Лучшее ИИ Радио в эфире! Оставайтесь с нами.",
        "Вы слушаете Лучшее ИИ Радио — где технологии встречаются с музыкой.",
    ],
    "en": [
        "Welcome to Лучшее ИИ Радио! Your source of music and news, twenty-four seven.",
        "This is Лучшее ИИ Радио. Automated. Infinite. Just for you.",
        "Лучшее ИИ Радио on the air! Stay with us.",
        "You're listening to Лучшее ИИ Радио, where tech meets music.",
    ],
    "sr": [
        "Dobrodošli na Лучшее ИИ Радио! Vaš izvor muzike i informacija, dvadeset četiri sata.",
        "Ovo je Лучшее ИИ Радио. Automatizovano. Beskonačno. Samo za vas.",
        "Лучшее ИИ Радио na talasima! Ostanite s nama.",
        "Slušate Лучшее ИИ Радио, gdje tehnologija sreće muziku.",
    ],
}
OUTRO_TEXTS = {
    "ru": [
        "Это были новости. Продолжайте слушать.",
        "Спасибо, что были с нами. Возвращаемся к музыке.",
        "Лучшее ИИ Радио продолжает программу.",
        "Оставайтесь на волне, после музыки вернёмся.",
    ],
    "en": [
        "That was the news. Keep listening.",
        "Thanks for being with us. Music is back.",
        "Лучшее ИИ Радио continues the program.",
        "Stay tuned, we'll be back after the music.",
    ],
    "sr": [
        "To su bile vijesti. Nastavite da nas slušate.",
        "Hvala što ste bili s nama. Muzika se vraća.",
        "Лучшее ИИ Радио nastavlja sa programom.",
        "Ostanite na vezi, vraćamo se nakon muzike.",
    ],
}
TIME_TEMPLATES = {
    "ru": ["Сейчас {time}.", "Время {time}. Вы слушаете Лучшее ИИ Радио.", "На Лучшее ИИ Радио сейчас {time}."],
    "en": ["The time is {time}.", "It's {time}. You're listening to Лучшее ИИ Радио.", "On Лучшее ИИ Радио it's {time}."],
    "sr": ["Tačno je {time}.", "Vrijeme je {time}. Slušate Лучшее ИИ Радио.", "Na Лучшее ИИ Radiju je {time}."],
}

# Короткие реплики диджея между треками (когда нет новостей/погоды)
DJ_PHRASES_RU = [
    "Отличная песня! Следующий трек уже в эфире.",
    "Спасибо, что слушаете нас. Продолжаем.",
    "Приятной музыки! Оставайтесь на волне.",
    "Вот это выбор! Слушайте дальше.",
    "Лучшее ИИ Радио. Музыка без остановки.",
    "Надеюсь, вам заходит. Ещё один трек.",
    "Какая тема! Следующая композиция.",
    "Держитесь, не переключайтесь.",
    "Классно звучит. Продолжаем в том же духе.",
    "Вы слушаете Лучшее ИИ Радио. Музыка 24/7.",
    "Отличный трек. Что дальше?",
    "Спасибо за внимание. Ещё музыка.",
    "Вот так вот. Следующая песня.",
    "Приятного прослушивания. Остаёмся в эфире.",
    "Хорошая музыка никогда не заканчивается. Вот ещё.",
    "Лучшее ИИ Радио. Ваш звук.",
    "Зацените следующий трек.",
    "Оставайтесь с нами. Продолжаем.",
    "Ещё одна композиция для вас.",
    "Музыка на связи. Слушайте дальше.",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
