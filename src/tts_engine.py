"""
Pirate Radio AI - Text-to-Speech Engine
Uses Microsoft Edge TTS (free, high quality)
"""
import asyncio
import logging
import hashlib
from pathlib import Path
from typing import Optional
import edge_tts

import config

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech using Edge TTS"""
    
    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self.cache_dir = config.CACHE_DIR / "tts"
        self.cache_dir.mkdir(exist_ok=True)
        
    async def synthesize(
        self, 
        text: str, 
        voice: str = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        output_path: Path = None
    ) -> Path:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            voice: Edge TTS voice name (e.g., 'sr-RS-NicholasNeural')
            rate: Speech rate (e.g., '+10%', '-20%')
            pitch: Voice pitch (e.g., '+10Hz', '-5Hz')
            output_path: Where to save the audio
            
        Returns:
            Path to the generated audio file
        """
        voice = voice or config.VOICE_NEWS
        
        # Check cache
        if self.cache_enabled:
            cache_key = self._get_cache_key(text, voice, rate, pitch)
            cached_path = self.cache_dir / f"{cache_key}.mp3"
            if cached_path.exists():
                logger.debug(f"Using cached TTS: {cache_key}")
                return cached_path
        
        # Generate output path (use stable hash to avoid collisions)
        if output_path is None:
            cache_key = self._get_cache_key(text, voice, rate, pitch)
            output_path = config.OUTPUT_DIR / f"tts_{cache_key}.mp3"
        
        try:
            # Create communicate object
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
            )
            
            # Save to file
            await communicate.save(str(output_path))
            
            # Cache it
            if self.cache_enabled:
                import shutil
                shutil.copy(output_path, cached_path)
            
            logger.info(f"Generated TTS: {len(text)} chars -> {output_path.name}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    async def synthesize_ssml(self, ssml: str, output_path: Path) -> Path:
        """Synthesize SSML (limited support in edge-tts)"""
        # Edge TTS has limited SSML support
        # For now, just extract text and synthesize
        import re
        text = re.sub(r'<[^>]+>', '', ssml)
        return await self.synthesize(text, output_path=output_path)
    
    async def stream_synthesis(self, text: str, voice: str = None):
        """
        Stream TTS chunks (for real-time playback)
        
        Yields audio chunks as they're generated
        """
        voice = voice or config.VOICE_NEWS
        
        communicate = edge_tts.Communicate(text=text, voice=voice)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    
    def _get_cache_key(self, text: str, voice: str, rate: str, pitch: str) -> str:
        """Generate cache key for TTS"""
        content = f"{text}:{voice}:{rate}:{pitch}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    @staticmethod
    async def list_voices(language: str = None) -> list:
        """List available voices"""
        voices = await edge_tts.list_voices()
        
        if language:
            voices = [v for v in voices if v["Locale"].startswith(language)]
            
        return voices
    
    async def generate_jingle(self, text: str = None) -> Path:
        """Generate a radio jingle"""
        import random
        text = text or random.choice(config.JINGLE_TEXTS)
        
        return await self.synthesize(
            text=text,
            voice=config.VOICE_JINGLE,
            rate="+10%",  # Slightly faster for jingles
            output_path=config.OUTPUT_DIR / "jingle.mp3"
        )
    
    async def generate_news_audio(self, script: str) -> Path:
        """Generate news segment audio"""
        return await self.synthesize(
            text=script,
            voice=config.VOICE_NEWS,
            rate="+5%",  # Slightly faster news reading
            output_path=config.OUTPUT_DIR / "news_segment.mp3"
        )
    
    async def generate_weather_audio(self, script: str) -> Path:
        """Generate weather report audio"""
        return await self.synthesize(
            text=script,
            voice=config.VOICE_WEATHER,
            rate="+0%",
            output_path=config.OUTPUT_DIR / "weather.mp3"
        )


class VoiceSelector:
    """Helper to select appropriate voices"""
    
    VOICE_MAP = {
        # Serbian
        "sr": {
            "male": "sr-RS-NicholasNeural",
            "female": "sr-RS-SophieNeural",
        },
        # Croatian
        "hr": {
            "male": "hr-HR-SreckoNeural",
            "female": "hr-HR-GabrijelaNeural",
        },
        # English US
        "en-US": {
            "male": "en-US-GuyNeural",
            "female": "en-US-JennyNeural",
        },
        # English UK
        "en-GB": {
            "male": "en-GB-RyanNeural",
            "female": "en-GB-SoniaNeural",
        },
        # German
        "de": {
            "male": "de-DE-ConradNeural",
            "female": "de-DE-KatjaNeural",
        },
        # Russian
        "ru": {
            "male": "ru-RU-DmitryNeural",
            "female": "ru-RU-SvetlanaNeural",
        },
    }
    
    @classmethod
    def get_voice(cls, language: str, gender: str = "male") -> str:
        """Get voice for language and gender"""
        lang_key = language.split("-")[0] if "-" not in language[:2] else language[:5]
        voices = cls.VOICE_MAP.get(lang_key, cls.VOICE_MAP.get(language[:2], cls.VOICE_MAP["en-US"]))
        return voices.get(gender, voices["male"])


# Test
async def main():
    tts = TTSEngine()
    
    # List Serbian voices
    print("=== SERBIAN VOICES ===")
    voices = await TTSEngine.list_voices("sr")
    for v in voices:
        print(f"  {v['ShortName']}: {v['Gender']}")
    
    # Test synthesis
    print("\n=== TEST SYNTHESIS ===")
    test_text = "Dobrodošli na Pirate AI Radio. Ovo je test sinteze govora."
    
    output = await tts.synthesize(test_text)
    print(f"Generated: {output}")
    
    # Test jingle
    print("\n=== TEST JINGLE ===")
    jingle = await tts.generate_jingle()
    print(f"Jingle: {jingle}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
