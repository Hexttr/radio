"""
Pirate Radio AI - Stream Server
Один источник (playlist) → каждый слушатель получает одинаковый поток.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, AsyncIterator
from collections import deque

import config

logger = logging.getLogger(__name__)


class SimpleHTTPStreamer:
    """
    HTTP stream: один продюсер читает плейлист и рассылает чанки всем слушателям.
    Важно: reconnect на клиенте создаёт новое подключение → попадание в середину файла.
    Поэтому клиент должен минимизировать reconnect.
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.playlist: deque = deque()
        self._listeners: set = set()
        self._lock = asyncio.Lock()
        
    async def start(self):
        from aiohttp import web
        
        app = web.Application()
        app.router.add_get('/stream', self._handle_stream)
        app.router.add_get('/status', self._handle_status)
        app.router.add_get('/', self._handle_index)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        asyncio.create_task(self._broadcast_loop())
        
        logger.info(f"HTTP stream on port {self.port}, listen: http://localhost:{self.port}/stream")
    
    async def _broadcast_loop(self):
        """Читает плейлист и рассылает каждому слушателю. Плейлист потребляется только здесь."""
        silence = config.OUTPUT_DIR / "silence.mp3"
        
        while True:
            try:
                async with self._lock:
                    n = len(self._listeners)
                if n == 0:
                    await asyncio.sleep(0.5)
                    continue
                
                if self.playlist:
                    path = self.playlist.popleft()
                    try:
                        sz = path.stat().st_size if path.exists() else 0
                    except OSError:
                        sz = 0
                    logger.info(f"▶️ PLAY: {path.name} ({sz} bytes)")
                    async for chunk in self._read_file(path):
                        async with self._lock:
                            live = set(self._listeners)
                        failed = set()
                        for resp in live:
                            try:
                                await resp.write(chunk)
                            except Exception:
                                failed.add(resp)
                        if failed:
                            async with self._lock:
                                self._listeners -= failed
                else:
                    if silence.exists():
                        async for chunk in self._read_file(silence):
                            async with self._lock:
                                live = set(self._listeners)
                            for resp in live:
                                try:
                                    await resp.write(chunk)
                                except Exception:
                                    pass
                            if self.playlist:
                                break
                    else:
                        silence.parent.mkdir(exist_ok=True)
                        await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Broadcast: {e}")
                await asyncio.sleep(1)
    
    async def _handle_stream(self, request):
        from aiohttp import web
        
        resp = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': 'audio/mpeg',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'icy-name': config.RADIO_NAME,
            }
        )
        await resp.prepare(request)
        
        async with self._lock:
            self._listeners.add(resp)
        
        try:
            while True:
                await asyncio.sleep(3600)
        except (asyncio.CancelledError, ConnectionResetError, OSError):
            pass
        finally:
            async with self._lock:
                self._listeners.discard(resp)
        return resp
    
    async def _read_file(self, path: Path) -> AsyncIterator[bytes]:
        """Читает файл чанками в темпе ~realtime."""
        chunk_size = 65536
        # 128kbps = 16 KB/s → 64KB chunk ≈ 4 sec реального времени
        delay = (chunk_size / (config.STREAM_BITRATE * 125)) * 0.7
        
        try:
            with open(path, 'rb') as f:
                loop = asyncio.get_event_loop()
                while True:
                    data = await loop.run_in_executor(None, lambda: f.read(chunk_size))
                    if not data:
                        break
                    yield data
                    if len(data) == chunk_size:
                        await asyncio.sleep(delay)
        except FileNotFoundError:
            logger.warning(f"File not found: {path}")
        except Exception as e:
            logger.error(f"Read error {path}: {e}")
    
    def add_to_playlist(self, path: Path):
        if path and path.exists():
            self.playlist.append(path)
            logger.info(f"➕ ADD: {path.name} (queue={len(self.playlist)})")
        else:
            logger.warning(f"✖️ SKIP (missing): {path}")
    
    async def _handle_status(self, request):
        from aiohttp import web
        return web.json_response({
            "name": config.RADIO_NAME,
            "playlist_length": len(self.playlist),
        })
    
    async def _handle_index(self, request):
        from aiohttp import web
        html = f'''<!DOCTYPE html>
<html>
<head><title>{config.RADIO_NAME}</title>
<style>
body {{ font-family: Arial; background: #1a1a2e; color: white; min-height: 100vh; margin: 0; display: flex; justify-content: center; align-items: center; }}
.player {{ text-align: center; padding: 40px; }}
audio {{ width: 300px; margin: 20px; }}
</style>
</head>
<body><div class="player">
<h1>{config.RADIO_NAME}</h1>
<p>{config.RADIO_DESCRIPTION}</p>
<audio id="radio" controls autoplay>
  <source src="/stream" type="audio/mpeg">
</audio>
<p id="status">Queue: -</p>
</div>
<script>
const a = document.getElementById('radio');
a.addEventListener('error', () => {{ setTimeout(() => {{ a.src = '/stream?r=' + Date.now(); a.play(); }}, 3000); }});
setInterval(async () => {{
  try {{ const r = await fetch('/status'); const d = await r.json(); document.getElementById('status').textContent = 'Queue: ' + d.playlist_length; }} catch(e) {{}}
}}, 5000);
</script>
</body>
</html>'''
        return web.Response(text=html, content_type='text/html')


# Для тестов
async def main():
    streamer = SimpleHTTPStreamer(port=8080)
    await streamer.start()
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
