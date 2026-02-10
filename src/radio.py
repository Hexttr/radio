#!/usr/bin/env python3
"""
Pirate Radio AI - Main Orchestrator
The brain that coordinates everything
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import config
from src.scraper import NewsScraper, WeatherFetcher
from src.ai_writer import AIWriter
from src.tts_engine import TTSEngine
from src.audio_mixer import AudioMixer, MusicDownloader
from src.stream import SimpleHTTPStreamer

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger("PirateRadio")


class PirateRadio:
    """
    Main orchestrator for Pirate AI Radio
    
    Coordinates all components:
    - Scrapes news periodically
    - Generates AI scripts
    - Converts to speech
    - Mixes with music
    - Streams 24/7
    """
    
    def __init__(self):
        self.scraper = NewsScraper()
        self.weather = WeatherFetcher()
        self.writer = AIWriter()
        self.tts = TTSEngine()
        self.mixer = AudioMixer()
        self.streamer = SimpleHTTPStreamer(port=8080)
        
        self.is_running = False
        self.last_news_time: Optional[datetime] = None
        self.last_weather_time: Optional[datetime] = None
        
        # Tasks
        self._news_task: Optional[asyncio.Task] = None
        self._weather_task: Optional[asyncio.Task] = None
        self._music_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the radio station"""
        logger.info("=" * 50)
        logger.info(f"🏴‍☠️ Starting {config.RADIO_NAME}")
        logger.info("=" * 50)
        
        self.is_running = True
        
        # Initialize
        await self._initialize()
        
        # Start stream server
        await self.streamer.start()
        
        # Start background tasks
        self._news_task = asyncio.create_task(self._news_loop())
        self._weather_task = asyncio.create_task(self._weather_loop())
        self._music_task = asyncio.create_task(self._music_loop())
        
        # Generate initial content
        await self._generate_jingle()
        await self._generate_intro()
        
        logger.info(f"📻 Radio is LIVE at http://localhost:8080")
        
        # Wait for shutdown
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the radio station"""
        logger.info("Shutting down radio station...")
        self.is_running = False
        
        # Cancel tasks
        for task in [self._news_task, self._weather_task, self._music_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Radio station stopped")
    
    async def _initialize(self):
        """Initialize components"""
        # Create directories
        config.MUSIC_DIR.mkdir(exist_ok=True)
        config.OUTPUT_DIR.mkdir(exist_ok=True)
        config.CACHE_DIR.mkdir(exist_ok=True)
        
        # Download sample music if none exists
        if not list(config.MUSIC_DIR.glob("*.mp3")):
            logger.info("No music found, generating sample...")
            await MusicDownloader.download_sample_music()
    
    async def _generate_jingle(self) -> Path:
        """Generate and queue a jingle"""
        logger.info("Generating jingle...")
        jingle_path = await self.tts.generate_jingle()
        self.streamer.add_to_playlist(jingle_path)
        return jingle_path
    
    async def _generate_intro(self):
        """Generate intro announcement"""
        intro_text = await self.writer.generate_intro()
        intro_audio = await self.tts.synthesize(
            intro_text,
            output_path=config.OUTPUT_DIR / "intro.mp3"
        )
        self.streamer.add_to_playlist(intro_audio)
    
    async def _news_loop(self):
        """Background task: Generate news periodically"""
        while self.is_running:
            try:
                # Check if it's time for news
                now = datetime.now()
                if (self.last_news_time is None or 
                    now - self.last_news_time > timedelta(seconds=config.NEWS_INTERVAL)):
                    
                    await self._generate_news_segment()
                    self.last_news_time = now
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"News loop error: {e}")
                await asyncio.sleep(60)
    
    async def _generate_news_segment(self):
        """Generate a complete news segment"""
        logger.info("📰 Generating news segment...")
        
        try:
            # 1. Scrape news
            async with NewsScraper() as scraper:
                news_items = await scraper.fetch_all()
            
            if not news_items:
                logger.warning("No news items found")
                return
            
            # 2. Generate script
            script = await self.writer.generate_news_segment(news_items[:5])
            logger.debug(f"News script: {script[:100]}...")
            
            # 3. Convert to speech
            news_audio = await self.tts.generate_news_audio(script)
            
            # 4. Add jingle before news
            jingle = await self.tts.generate_jingle("Vijesti na Pirate Radiju.")
            
            # 5. Mix with background music
            mixed_audio = await self.mixer.mix_voice_with_music(
                news_audio,
                music_volume=0.15  # Lower music for news
            )
            
            # 6. Queue: Jingle -> News
            self.streamer.add_to_playlist(jingle)
            self.streamer.add_to_playlist(mixed_audio)
            
            logger.info("✅ News segment queued")
            
        except Exception as e:
            logger.error(f"News generation failed: {e}")
    
    async def _weather_loop(self):
        """Background task: Generate weather periodically"""
        while self.is_running:
            try:
                now = datetime.now()
                if (self.last_weather_time is None or
                    now - self.last_weather_time > timedelta(seconds=config.WEATHER_INTERVAL)):
                    
                    await self._generate_weather_segment()
                    self.last_weather_time = now
                
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Weather loop error: {e}")
                await asyncio.sleep(60)
    
    async def _generate_weather_segment(self):
        """Generate weather report"""
        logger.info("🌤️ Generating weather report...")
        
        try:
            # 1. Fetch weather
            async with WeatherFetcher() as fetcher:
                weather_data = await fetcher.get_weather()
            
            if not weather_data:
                return
            
            # 2. Generate script
            script = await self.writer.generate_weather_report(weather_data)
            
            # 3. Convert to speech
            weather_audio = await self.tts.generate_weather_audio(script)
            
            # 4. Queue
            self.streamer.add_to_playlist(weather_audio)
            
            logger.info("✅ Weather segment queued")
            
        except Exception as e:
            logger.error(f"Weather generation failed: {e}")
    
    async def _music_loop(self):
        """Background task: Keep music playing"""
        while self.is_running:
            try:
                # If playlist is getting low, add music
                if len(self.streamer.playlist) < 3:
                    await self._add_music_track()
                
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Music loop error: {e}")
                await asyncio.sleep(10)
    
    async def _add_music_track(self):
        """Add a music track to playlist"""
        music_files = self.mixer.get_music_library()
        
        if not music_files:
            # Generate silence if no music (add your tracks to music/ folder)
            silence_path = config.OUTPUT_DIR / "silence.mp3"
            if not silence_path.exists():
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "ffmpeg", "-y",
                        "-f", "lavfi",
                        "-i", "anullsrc=r=44100:cl=stereo",
                        "-t", "30",
                        "-c:a", "libmp3lame",
                        str(silence_path),
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await proc.wait()
                except FileNotFoundError:
                    logger.warning("FFmpeg not found. Install FFmpeg for full playback. Add MP3 files to music/.")
                    return
            if silence_path.exists():
                self.streamer.add_to_playlist(silence_path)
            return
        
        import random
        track = random.choice(music_files)
        
        # Prepare track (fade in/out)
        prepared = await self.mixer.prepare_music_track(track)
        self.streamer.add_to_playlist(prepared)
        
        logger.debug(f"🎵 Added music: {track.name}")
    
    async def generate_time_announcement(self):
        """Generate current time announcement"""
        text = await self.writer.generate_time_announcement()
        audio = await self.tts.synthesize(
            text,
            output_path=config.OUTPUT_DIR / "time.mp3"
        )
        self.streamer.add_to_playlist(audio)


async def main():
    """Main entry point"""
    radio = PirateRadio()
    
    # Handle shutdown signals (SIGTERM not on Windows)
    try:
        loop = asyncio.get_running_loop()
        def shutdown_handler():
            logger.info("Received shutdown signal")
            asyncio.create_task(radio.stop())
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, shutdown_handler)
    except NotImplementedError:
        pass  # Windows: use Ctrl+C only
    
    try:
        await radio.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    finally:
        await radio.stop()


if __name__ == "__main__":
    asyncio.run(main())
