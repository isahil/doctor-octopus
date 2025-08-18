import os
import aiofiles
import asyncio
from src.utils.logger import logger


stream_tasks = {}


async def start_streaming_log_file(sio, sid, subscription, log_file_path):
    file_exists = os.path.exists(log_file_path)
    if not file_exists:
        with open(log_file_path, "w"):
            pass
    if not stream_tasks.get(sid):
        stream_task = asyncio.create_task(stream_log_file(sio, sid, subscription, log_file_path))
        stream_tasks[sid] = stream_task
    else:
        logger.info(f"Stream task already exists for {sid}")


async def stream_log_file(sio, sid, subscription, log_file_path):
    async with aiofiles.open(log_file_path, "r", encoding="utf-8") as log_file:
        while True:
            line = await log_file.readline()
            if line:
                await sio.emit(subscription, line, room=sid)
    await asyncio.sleep(1)


async def stop_streaming_log_file(sid):
    if stream_tasks.get(sid):
        stream_task = stream_tasks.pop(sid)
        stream_task.cancel()
        logger.info(f"Stopped streaming log file for {sid}")
    else:
        logger.info(f"No stream task found for {sid}")
