import os
import aiofiles
import asyncio

stream_tasks = {}


async def start_streaming_log_file(sio, sid, subscription, log_file_path):
    file_exists = os.path.exists(log_file_path)
    if not file_exists:
        with open(log_file_path, "w") as f:
            pass
    if not stream_tasks.get(sid):
        stream_task = asyncio.create_task(stream_log_file(sio, sid, subscription, log_file_path))
        stream_tasks[sid] = stream_task
    else:
        print(f"Stream task already exists for {sid}")


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
        print(f"Stopped streaming log file for {sid}")
    else:
        print(f"No stream task found for {sid}")
