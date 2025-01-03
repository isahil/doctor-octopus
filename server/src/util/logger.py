import os
import aiofiles
import asyncio
from src.socketio import sio

async def stream_log_file(log_file_path):
        file_exists = os.path.exists(log_file_path)
        if not file_exists:
            with open(log_file_path, "w") as f:
                pass
        async with aiofiles.open(log_file_path, "r") as log_file:
            while True:
                line = await log_file.readline()
                if line:
                    await sio.emit('log', line)
        await asyncio.sleep(1)