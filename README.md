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

## 🚀 Quick Start

```bash
# 1. Clone i setup
git clone https://github.com/yourname/pirate-radio-ai
cd pirate-radio-ai

# 2. Kreiraj .env fajl
cp .env.example .env
# Dodaj GROQ_API_KEY (besplatan na console.groq.com)

# 3. Pokreni sa Docker
docker-compose up -d

# 4. Slušaj na
# http://localhost:8000/stream
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

## 📻 Stream URL-ovi

- **Direct Stream:** `http://your-ip:8000/stream`
- **Playlist:** `http://your-ip:8000/stream.m3u`
- **Status:** `http://your-ip:8000/status-json.xsl`

## 🆓 Besplatni Servisi

| Servis | Korištenje | Limit |
|--------|-----------|-------|
| Groq API | LLM (Llama 70B) | 30 req/min |
| Edge TTS | Text-to-Speech | Neograničeno* |
| Oracle ARM | Server | 24GB RAM, zauvijek |

*Fair use, ne zloupotrbljavaj

## 📝 License

MIT - Koristi kako hoćeš!
