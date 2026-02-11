"""
Pirate Radio AI - Audio Mixer
Mixes voice segments with background music using FFmpeg
"""
import asyncio
import logging
import random
import subprocess
import uuid
from pathlib import Path
from typing import List, Optional
import shutil

import config

logger = logging.getLogger(__name__)


class AudioMixer:
    """Mix audio segments with background music"""
    
    def __init__(self):
        self.music_dir = config.MUSIC_DIR
        self.output_dir = config.OUTPUT_DIR
        self._ffmpeg_ok = None  # Lazy check
        
    def _verify_ffmpeg(self) -> bool:
        """Check if FFmpeg is available (lazy). Returns True if OK."""
        if self._ffmpeg_ok is None:
            try:
                subprocess.run([config.FFMPEG_CMD, "-version"], capture_output=True, check=True)
                self._ffmpeg_ok = True
                logger.debug("FFmpeg found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self._ffmpeg_ok = False
                logger.warning("FFmpeg not found. Set FFMPEG_BIN_DIR in .env or PATH. https://ffmpeg.org")
        return self._ffmpeg_ok
    
    async def mix_voice_with_music(
        self,
        voice_path: Path,
        music_path: Path = None,
        output_path: Path = None,
        music_volume: float = None
    ) -> Path:
        """
        Mix voice with background music
        
        Args:
            voice_path: Path to voice audio
            music_path: Path to background music (random if None)
            output_path: Output file path
            music_volume: Music volume (0.0-1.0)
        """
        music_volume = music_volume or config.MUSIC_VOLUME
        output_path = output_path or self.output_dir / "mixed_segment.mp3"
        
        if not self._verify_ffmpeg():
            shutil.copy(voice_path, output_path)
            return output_path
        
        # Get music if not specified
        if music_path is None:
            music_path = self._get_random_music()
            
        if music_path is None:
            # No music available, just return voice
            shutil.copy(voice_path, output_path)
            return output_path
        
        # Get voice duration
        voice_duration = await self._get_duration(voice_path)
        fade_out_start = max(0.0, voice_duration - 2)
        
        # FFmpeg command to mix audio
        # Voice at full volume, music lowered
        cmd = [
            config.FFMPEG_CMD, "-y",
            "-i", str(voice_path),
            "-i", str(music_path),
            "-filter_complex",
            f"[1:a]volume={music_volume},afade=t=in:st=0:d=2,afade=t=out:st={fade_out_start}:d=2[music];"
            f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[out]",
            "-map", "[out]",
            "-ac", "2",
            "-ar", "44100",
            "-b:a", f"{config.STREAM_BITRATE}k",
            str(output_path)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                # Fallback: just use voice
                shutil.copy(voice_path, output_path)
            else:
                logger.info(f"Mixed audio: {output_path.name}")
                
        except Exception as e:
            logger.error(f"Mix error: {e}")
            shutil.copy(voice_path, output_path)
            
        return output_path
    
    async def concatenate_audio(
        self,
        audio_files: List[Path],
        output_path: Path = None,
        crossfade: float = None
    ) -> Path:
        """
        Concatenate multiple audio files
        
        Args:
            audio_files: List of audio file paths
            output_path: Output file path
            crossfade: Crossfade duration in seconds
        """
        crossfade = crossfade or config.CROSSFADE_DURATION
        output_path = output_path or self.output_dir / "concatenated.mp3"
        
        if len(audio_files) == 0:
            raise ValueError("No audio files to concatenate")
            
        if len(audio_files) == 1:
            shutil.copy(audio_files[0], output_path)
            return output_path
        
        # Create file list for FFmpeg
        list_file = self.output_dir / "concat_list.txt"
        with open(list_file, "w") as f:
            for audio in audio_files:
                f.write(f"file '{audio.absolute()}'\n")
        
        # FFmpeg concat
        cmd = [
            config.FFMPEG_CMD, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c:a", "libmp3lame",
            "-b:a", f"{config.STREAM_BITRATE}k",
            str(output_path)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Concatenated {len(audio_files)} files -> {output_path.name}")
            else:
                logger.error("Concatenation failed")
                
        finally:
            list_file.unlink(missing_ok=True)
            
        return output_path
    
    async def create_radio_segment(
        self,
        jingle_path: Path,
        voice_path: Path,
        outro_path: Path = None,
        music_path: Path = None
    ) -> Path:
        """
        Create a complete radio segment:
        [Jingle] -> [Voice with music] -> [Outro]
        """
        segments = []
        
        # Add jingle
        if jingle_path and jingle_path.exists():
            segments.append(jingle_path)
        
        # Mix voice with music
        if voice_path and voice_path.exists():
            mixed = await self.mix_voice_with_music(
                voice_path,
                music_path,
                self.output_dir / "voice_mixed.mp3"
            )
            segments.append(mixed)
        
        # Add outro
        if outro_path and outro_path.exists():
            segments.append(outro_path)
        
        # Concatenate all
        if segments:
            return await self.concatenate_audio(
                segments,
                self.output_dir / "radio_segment.mp3"
            )
            
        raise ValueError("No segments to create")
    
    async def prepare_music_track(
        self,
        music_path: Path,
        duration: float = None,
        fade_in: float = 2,
        fade_out: float = 2
    ) -> Path:
        """Prepare a music track with fades and optional trimming"""
        if not self._verify_ffmpeg():
            return music_path  # Return as-is if no FFmpeg
        duration = duration or config.MUSIC_TRACK_LENGTH
        output_path = self.output_dir / f"music_{music_path.stem}_{uuid.uuid4().hex[:8]}.mp3"
        
        # Build filter
        filters = []
        if fade_in:
            filters.append(f"afade=t=in:st=0:d={fade_in}")
        if fade_out:
            filters.append(f"afade=t=out:st={duration-fade_out}:d={fade_out}")
            
        filter_str = ",".join(filters) if filters else "anull"
        
        cmd = [
            config.FFMPEG_CMD, "-y",
            "-i", str(music_path),
            "-t", str(duration),
            "-af", filter_str,
            "-c:a", "libmp3lame",
            "-b:a", f"{config.STREAM_BITRATE}k",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        return output_path
    
    async def _get_duration(self, audio_path: Path) -> float:
        """Get audio file duration in seconds"""
        cmd = [
            config.FFPROBE_CMD,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 60.0  # Default
    
    def _get_random_music(self) -> Optional[Path]:
        """Get a random music file from the library"""
        music_files = list(self.music_dir.glob("*.mp3"))
        music_files.extend(self.music_dir.glob("*.wav"))
        music_files.extend(self.music_dir.glob("*.ogg"))
        
        if music_files:
            return random.choice(music_files)
        return None
    
    def get_music_library(self) -> List[Path]:
        """List all music files"""
        files = []
        for ext in ["*.mp3", "*.wav", "*.ogg", "*.flac"]:
            files.extend(self.music_dir.glob(ext))
        return sorted(files)


class MusicDownloader:
    """Download royalty-free music"""
    
    # Free music sources (all royalty-free)
    LOFI_URLS = [
        # These are example URLs - replace with actual royalty-free sources
        # Freesound, Pixabay Music, etc.
    ]
    
    @staticmethod
    async def download_sample_music():
        """Download some sample royalty-free music"""
        import aiohttp
        
        # Create a simple sine wave as fallback
        music_dir = config.MUSIC_DIR
        sample_path = music_dir / "sample_beat.mp3"
        
        if not sample_path.exists():
            # Generate a simple beat using FFmpeg
            cmd = [
                config.FFMPEG_CMD, "-y",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=180",  # 3 min tone
                "-c:a", "libmp3lame",
                "-b:a", "128k",
                str(sample_path)
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                logger.info("Generated sample audio")
            except Exception as e:
                logger.error(f"Could not generate sample: {e}")


# Test
async def main():
    mixer = AudioMixer()
    
    # Download sample music
    await MusicDownloader.download_sample_music()
    
    print("Music library:", mixer.get_music_library())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
