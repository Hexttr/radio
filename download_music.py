#!/usr/bin/env python3
"""
Pirate Radio AI - Free Music Downloader
Downloads royalty-free music from free sources

MUZIKA JE 100% BESPLATNA I LEGALNA:
- Pixabay Music: CC0 (public domain)
- Free Music Archive: Various CC licenses
- Incompetech: Royalty-free with attribution
"""
import asyncio
import aiohttp
import os
import subprocess
from pathlib import Path

MUSIC_DIR = Path(__file__).parent / "music"
MUSIC_DIR.mkdir(exist_ok=True)

# =============================================================================
# FREE MUSIC SOURCES - All Creative Commons or Public Domain
# =============================================================================

# Pixabay Music - CC0 License (no attribution required)
# These are direct CDN links that work
PIXABAY_TRACKS = {
    "lofi_study": "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "chill_abstract": "https://cdn.pixabay.com/audio/2022/01/18/audio_d0a13f69d2.mp3", 
    "ambient_piano": "https://cdn.pixabay.com/audio/2022/08/04/audio_2dde668d05.mp3",
    "electronic_future": "https://cdn.pixabay.com/audio/2022/10/14/audio_1a6a9d9212.mp3",
    "jazzy_night": "https://cdn.pixabay.com/audio/2023/07/30/audio_e6c3ae0fdc.mp3",
    "soft_corporate": "https://cdn.pixabay.com/audio/2022/03/15/audio_8cb749bf51.mp3",
    "inspiring_cinematic": "https://cdn.pixabay.com/audio/2022/11/22/audio_a1b958de3f.mp3",
    "relaxing_guitar": "https://cdn.pixabay.com/audio/2023/09/19/audio_8eba2a25d0.mp3",
}

# Free Music Archive - Various CC licenses (check individual tracks)
# Format: YouTube audio IDs that can be downloaded via yt-dlp
FMA_PLAYLISTS = [
    # Lo-Fi Hip Hop
    "https://freemusicarchive.org/genre/Lo-fi/",
    # Electronic
    "https://freemusicarchive.org/genre/Electronic/",
]

# Internet Archive - Public domain music
ARCHIVE_ORG_TRACKS = {
    "classical_piano": "https://archive.org/download/Chopin_Nocturnes_Opus_9/Chopin_Nocturne_Op9_No2.mp3",
    "jazz_standard": "https://archive.org/download/78_take-the-a-train_duke-ellington-and-his-famous-orchestra-billy-strayhorn_gbia0002316/Take%20The%20A%20Train%20-%20Duke%20Ellington%20And%20His%20Famous%20Orchestra.mp3",
}

# Combine all sources
FREE_MUSIC_SOURCES = {
    **PIXABAY_TRACKS,
    **ARCHIVE_ORG_TRACKS,
}

# Note: These URLs might change. If downloads fail, visit:
# - https://pixabay.com/music/
# - https://freesound.org/
# - https://incompetech.com/music/
# And download manually to the 'music' folder


async def download_file(session: aiohttp.ClientSession, url: str, filename: str) -> bool:
    """Download a single file"""
    filepath = MUSIC_DIR / filename
    
    if filepath.exists():
        print(f"  ✓ {filename} already exists")
        return True
    
    try:
        print(f"  ↓ Downloading {filename}...")
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f"  ✓ {filename} downloaded ({len(content) // 1024} KB)")
                return True
            else:
                print(f"  ✗ {filename} failed (HTTP {response.status})")
                return False
    except Exception as e:
        print(f"  ✗ {filename} error: {e}")
        return False


async def download_all():
    """Download all free music"""
    print("🎵 Pirate Radio AI - Free Music Downloader")
    print("=" * 40)
    print(f"Downloading to: {MUSIC_DIR.absolute()}")
    print()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, url in FREE_MUSIC_SOURCES.items():
            tasks.append(download_file(session, url, f"{name}.mp3"))
        
        results = await asyncio.gather(*tasks)
        
    success = sum(results)
    print()
    print(f"Downloaded {success}/{len(FREE_MUSIC_SOURCES)} tracks")
    
    if success < len(FREE_MUSIC_SOURCES):
        print()
        print("Some downloads failed. You can manually download music from:")
        print("  - https://pixabay.com/music/")
        print("  - https://freesound.org/")
        print("  - https://incompetech.com/music/")
        print(f"  Place MP3 files in: {MUSIC_DIR.absolute()}")


def generate_test_tones():
    """Generate test tones using FFmpeg (fallback if downloads fail)"""
    import subprocess
    
    print()
    print("Generating test audio files...")
    
    test_files = [
        ("test_tone_440hz.mp3", "sine=frequency=440:duration=60"),
        ("test_tone_880hz.mp3", "sine=frequency=880:duration=60"),
        ("white_noise.mp3", "anoisesrc=d=60:c=white:a=0.5"),
    ]
    
    for filename, filter_str in test_files:
        filepath = MUSIC_DIR / filename
        if filepath.exists():
            print(f"  ✓ {filename} exists")
            continue
            
        try:
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", filter_str,
                "-c:a", "libmp3lame",
                "-b:a", "128k",
                str(filepath)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ Generated {filename}")
        except Exception as e:
            print(f"  ✗ Failed to generate {filename}: {e}")


if __name__ == "__main__":
    asyncio.run(download_all())
    
    # Check if any music exists
    music_files = list(MUSIC_DIR.glob("*.mp3"))
    if not music_files:
        print()
        print("No music files found. Generating test tones...")
        generate_test_tones()
    
    print()
    print("🎵 Music library ready!")
    print(f"   Location: {MUSIC_DIR.absolute()}")
    print(f"   Tracks: {len(list(MUSIC_DIR.glob('*.mp3')))}")
