"""
Pirate Radio AI - Stream Server
Streams audio to Icecast using FFmpeg
"""
import asyncio
import logging
import signal
from pathlib import Path
from typing import Optional, AsyncIterator
from collections import deque

import config

logger = logging.getLogger(__name__)


class IcecastStreamer:
    """Stream audio to Icecast server using FFmpeg"""
    
    def __init__(self):
        self.process: Optional[asyncio.subprocess.Process] = None
        self.is_streaming = False
        self.playlist: deque = deque()
        self._stop_event = asyncio.Event()
        
    async def start_stream(self):
        """Start the stream to Icecast"""
        if self.is_streaming:
            logger.warning("Stream already running")
            return
            
        self.is_streaming = True
        self._stop_event.clear()
        
        logger.info(f"Starting stream to {config.ICECAST_HOST}:{config.ICECAST_PORT}{config.ICECAST_MOUNT}")
        
        # Start the streaming loop
        await self._stream_loop()
    
    async def stop_stream(self):
        """Stop the stream"""
        self._stop_event.set()
        self.is_streaming = False
        
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
            self.process = None
            
        logger.info("Stream stopped")
    
    def add_to_playlist(self, audio_path: Path):
        """Add audio file to playlist"""
        if audio_path.exists():
            self.playlist.append(audio_path)
            logger.debug(f"Added to playlist: {audio_path.name}")
    
    def clear_playlist(self):
        """Clear the playlist"""
        self.playlist.clear()
    
    async def _stream_loop(self):
        """Main streaming loop"""
        while not self._stop_event.is_set():
            if self.playlist:
                audio_path = self.playlist.popleft()
                await self._stream_file(audio_path)
            else:
                # No audio in queue, wait a bit
                await asyncio.sleep(1)
    
    async def _stream_file(self, audio_path: Path):
        """Stream a single file to Icecast"""
        icecast_url = (
            f"icecast://source:{config.ICECAST_SOURCE_PASSWORD}@"
            f"{config.ICECAST_HOST}:{config.ICECAST_PORT}{config.ICECAST_MOUNT}"
        )
        
        cmd = [
            config.FFMPEG_CMD,
            "-re",  # Read at native speed
            "-i", str(audio_path),
            "-c:a", "libmp3lame",
            "-b:a", f"{config.STREAM_BITRATE}k",
            "-f", "mp3",
            "-content_type", "audio/mpeg",
            icecast_url
        ]
        
        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info(f"Streaming: {audio_path.name}")
            await self.process.wait()
            
        except asyncio.CancelledError:
            if self.process:
                self.process.terminate()
            raise
        except Exception as e:
            logger.error(f"Stream error: {e}")
        finally:
            self.process = None


class DirectStreamer:
    """Stream directly using FFmpeg (no Icecast needed)
    
    This creates a simple HTTP audio stream that clients can connect to.
    Good for testing or simple setups.
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.process: Optional[asyncio.subprocess.Process] = None
        self.is_streaming = False
        
    async def start_stream(self, playlist_file: Path):
        """
        Start streaming from a playlist file
        
        The playlist file should be a text file with one audio file per line.
        """
        if self.is_streaming:
            return
            
        self.is_streaming = True
        
        # Use FFmpeg to stream via HLS
        output_dir = config.OUTPUT_DIR / "hls"
        output_dir.mkdir(exist_ok=True)
        
        cmd = [
            config.FFMPEG_CMD,
            "-re",
            "-f", "concat",
            "-safe", "0",
            "-stream_loop", "-1",  # Loop forever
            "-i", str(playlist_file),
            "-c:a", "aac",
            "-b:a", f"{config.STREAM_BITRATE}k",
            "-f", "hls",
            "-hls_time", "10",
            "-hls_list_size", "6",
            "-hls_flags", "delete_segments",
            str(output_dir / "stream.m3u8")
        ]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        logger.info(f"HLS stream started at {output_dir / 'stream.m3u8'}")


class SimpleHTTPStreamer:
    """
    Very simple HTTP streamer using Python's built-in server
    Streams MP3 files directly
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.current_file: Optional[Path] = None
        self.playlist: deque = deque()
        
    async def start(self):
        """Start the HTTP server"""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_get('/stream', self._handle_stream)
        app.router.add_get('/status', self._handle_status)
        app.router.add_get('/', self._handle_index)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"HTTP stream server started on port {self.port}")
        logger.info(f"Listen at: http://localhost:{self.port}/stream")
    
    async def _handle_stream(self, request):
        """Handle stream requests"""
        from aiohttp import web
        
        response = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': 'audio/mpeg',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'icy-name': config.RADIO_NAME,
            }
        )
        await response.prepare(request)
        
        silence_path = config.OUTPUT_DIR / "silence.mp3"
        
        try:
            while True:
                if self.playlist:
                    audio_file = self.playlist[0]
                    async for chunk in self._read_audio_file(audio_file):
                        await response.write(chunk)
                    self.playlist.popleft()
                else:
                    # Бесконечный цикл тишины — никогда не останавливаем поток 24/7
                    while not self.playlist:
                        if silence_path.exists():
                            async for chunk in self._read_audio_file(silence_path):
                                await response.write(chunk)
                                if self.playlist:
                                    break
                            if self.playlist:
                                break
                        else:
                            # Создаём silence на лету если вдруг нет
                            silence_path.parent.mkdir(exist_ok=True)
                            await asyncio.sleep(0.1)
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Stream error: {e}")
            
        return response
    
    async def _read_audio_file(self, path: Path) -> AsyncIterator[bytes]:
        """Read audio file in chunks (non-blocking to avoid freezing the event loop)"""
        chunk_size = 65536  # 64KB — больше буфер, меньше стыков между чанками
        # Отправляем ~1.5x быстрее реального времени — буфер не опустошается на переходах
        bytes_per_sec = config.STREAM_BITRATE * 1000 / 8
        throttle = (chunk_size / bytes_per_sec) * 0.65  # ~1.5x скорость
        
        try:
            with open(path, 'rb') as f:
                loop = asyncio.get_event_loop()
                while True:
                    chunk = await loop.run_in_executor(None, lambda: f.read(chunk_size))
                    if not chunk:
                        break
                    yield chunk
                    # Не ждём после последнего чанка — сразу переходим к следующему файлу
                    if len(chunk) >= chunk_size:
                        await asyncio.sleep(throttle)
        except FileNotFoundError:
            logger.warning(f"Stream: file not found {path}")
        except Exception as e:
            logger.error(f"Stream read error: {e}")
    
    async def _handle_status(self, request):
        """Return stream status"""
        from aiohttp import web
        
        return web.json_response({
            "name": config.RADIO_NAME,
            "description": config.RADIO_DESCRIPTION,
            "playlist_length": len(self.playlist),
            "current": str(self.current_file) if self.current_file else None,
        })
    
    async def _handle_index(self, request):
        """Return simple HTML player"""
        from aiohttp import web
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.RADIO_NAME}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }}
                .player {{
                    text-align: center;
                    padding: 40px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }}
                h1 {{ margin-bottom: 10px; }}
                .emoji {{ font-size: 48px; margin-bottom: 20px; }}
                audio {{ width: 300px; margin-top: 20px; }}
                .status {{ margin-top: 20px; opacity: 0.7; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="player">
                <div class="emoji">🏴‍☠️📻</div>
                <h1>{config.RADIO_NAME}</h1>
                <p>{config.RADIO_DESCRIPTION}</p>
                <audio id="radio" controls autoplay preload="auto">
                    <source src="/stream" type="audio/mpeg">
                    Your browser does not support audio.
                </audio>
                <div class="status" id="status">Loading...</div>
            </div>
            <script>
                const audio = document.getElementById('radio');
                let reconnectTimeout = null;

                function reconnect() {{
                    if (reconnectTimeout) return;
                    reconnectTimeout = setTimeout(() => {{
                        reconnectTimeout = null;
                        audio.src = '/stream?t=' + Date.now();
                        audio.load();
                        audio.play().catch(() => {{}});
                    }}, 800);
                }}

                function tryPlay() {{
                    if (audio.paused) {{
                        audio.play().catch(() => reconnect());
                    }}
                }}

                audio.addEventListener('ended', reconnect);
                audio.addEventListener('stalled', reconnect);
                audio.addEventListener('error', reconnect);
                audio.addEventListener('waiting', () => {{ tryPlay(); }});
                audio.addEventListener('pause', () => {{
                    setTimeout(tryPlay, 1500);
                }});

                setInterval(tryPlay, 2500);

                setInterval(async () => {{
                    const res = await fetch('/status');
                    const data = await res.json();
                    document.getElementById('status').textContent = 
                        `Queue: ${{data.playlist_length}} tracks`;
                }}, 5000);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    def add_to_playlist(self, audio_path: Path):
        """Add audio to playlist"""
        if audio_path.exists():
            self.playlist.append(audio_path)


# Test
async def main():
    streamer = SimpleHTTPStreamer(port=8080)
    await streamer.start()
    
    # Keep running
    print("Stream server running on http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
