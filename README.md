# 🏴‍☠️ PIRATE RADIO AI

24/7 AI-generisana radio stanica koja automatski:
- Scrape-uje trending teme
- Generiše vijesti sa Llama (Groq API - besplatno)
- Pretvara u govor sa Edge TTS (besplatno)
- Mixa sa royalty-free muzikom
- Streama 24/7 na Icecast

## 🏗️ Arhitektura

```
┌─────────────────────────────────────────────────────────────┐
│                    PIRATE RADIO AI                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Scraper   │→ │  AI Writer  │→ │  TTS Engine │         │
│  │  (Reddit,   │  │   (Groq     │  │  (Edge TTS) │         │
│  │   RSS, API) │  │    Llama)   │  │             │         │
│  └─────────────┘  └─────────────┘  └──────┬──────┘         │
│                                           │                │
│  ┌─────────────┐  ┌─────────────┐  ┌──────▼──────┐         │
│  │   Music     │→ │   Mixer     │→ │   Stream    │→ 🌐     │
│  │   Library   │  │  (FFmpeg)   │  │  (Icecast)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 📖 Подробный гайд

**Пошаговая инструкция по запуску:** [LAUNCH.md](LAUNCH.md) — установка Python, FFmpeg, зависимости, настройка `.env`, музыка, запуск и пуш в GitHub.

---

## 🚀 Quick Start

### Windows (локально)

1. Установите **Python 3.10+**. Для микширования музыки и генерации тишины нужен **FFmpeg** ([скачать](https://ffmpeg.org), добавить в PATH); без него запустится только TTS и поток.
2. В папке проекта: `pip install -r requirements.txt`
3. (Опционально) В файле `.env` укажите `GROQ_API_KEY` — бесплатный ключ на [console.groq.com](https://console.groq.com) для AI-новостей.
4. Положите свои треки в папку **`music/`** (MP3, WAV, OGG, FLAC). Если папка пуста — между эфиром будет тишина, пока вы не добавите файлы.
5. Запуск: двойной клик по **`run.bat`** или в терминале:
   ```bash
   python -m src.radio
   ```
6. Откройте в браузере: **http://localhost:9090** — там плеер и поток `/stream`.

### Доступ из интернета (ngrok)

1. Скачайте [ngrok](https://ngrok.com/download), распакуйте и добавьте в PATH.
2. Получите authtoken на [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken).
3. Создайте `ngrok.yml` в папке проекта (см. `ngrok.yml.example`):
   ```yaml
   version: "2"
   authtoken: YOUR_TOKEN
   ```
4. Запуск: **`start-all.bat`** — поднимет радио и туннель. URL для слушателей появится в окне ngrok.

### Docker

```bash
# 1. Создайте .env и добавьте GROQ_API_KEY (по желанию)
# 2. Запуск
docker-compose up -d

# 3. Слушать
# http://localhost:8080/   (веб-плеер)
# http://localhost:8080/stream  (поток)
```

## 📁 Struktura

```
pirate-radio-ai/
├── src/
│   ├── scraper.py       # Scrape trending topics
│   ├── ai_writer.py     # Generate news with Llama
│   ├── tts_engine.py    # Text-to-speech (Edge TTS)
│   ├── audio_mixer.py   # Mix voice + music
│   ├── stream.py        # Icecast streaming
│   └── radio.py         # Main orchestrator
├── music/               # Royalty-free music
├── output/              # Generated audio segments
├── config.py            # Configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── setup.sh            # Oracle ARM setup script
```

## 🔧 Konfiguracija

```python
# config.py
RADIO_NAME = "Pirate AI Radio"
LANGUAGE = "sr-RS"  # Srpski
NEWS_INTERVAL = 15  # Vijesti svakih 15 minuta
MUSIC_VOLUME = 0.3  # Background music volume
```

## 🎤 Glasovi

Edge TTS podržava 300+ glasova. Za srpski:
- `sr-RS-NicholasNeural` (muški)
- `sr-RS-SophieNeural` (ženski)

Za engleski:
- `en-US-GuyNeural` (muški)
- `en-US-JennyNeural` (ženski)

## 📻 Адреса потока

- **Веб-плеер:** `http://localhost:8080/`
- **Поток MP3:** `http://localhost:8080/stream`
- **Статус (JSON):** `http://localhost:8080/status`

## 🆓 Besplatni Servisi

| Servis | Korištenje | Limit |
|--------|-----------|-------|
| Groq API | LLM (Llama 70B) | 30 req/min |
| Edge TTS | Text-to-Speech | Neograničeno* |
| Oracle ARM | Server | 24GB RAM, zauvijek |

*Fair use, ne zloupotrbljavaj

## 📝 License

MIT - Koristi kako hoćeš!
