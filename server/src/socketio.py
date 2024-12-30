import os
import sys
import asyncio
import socketio
sys.path.append("./src")
from fix_client import FixClient
import aiofiles
local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

sio = socketio.AsyncServer(cors_allowed_origins=origins,async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")

# fix_client = FixClient(env="qa", app="fix", fix_side="client", broadcast=True, sio=sio)
# client_app = asyncio.create_task(fix_client.start_mock_client())

# fix_dealer = FixClient(env="qa", app="fix", fix_side="dealer", broadcast=True, sio=sio)
# dealer_app = asyncio.create_task(fix_dealer.start_mock_client())

__all__ = ["socketio_app", "sio", "fix_client"]

sio_client_count = 0
log_file_path = f"{local_dir}/logs/doctor.log"

async def stream_log_file(log_file_path):
        async with aiofiles.open(log_file_path, "r") as log_file:
            while True:
                line = await log_file.readline()
                if line:
                    await sio.emit('log', line)
        await asyncio.sleep(1)

@sio.on('connect')
async def connect(sid, environ):
    global sio_client_count
    sio_client_count += 1
    print(f"\tConnected to client... [{sid}] | Clients connected: {sio_client_count}")
    await sio.emit('message', f'Hello from the FASTAPI W.S. server! | Clients connected: {sio_client_count}', room=sid)
    sio.start_background_task(stream_log_file, log_file_path) # start background task to stream the fix client log file
    # client_app = sio.start_background_task(fix_client.start_client) # start background task to connect to the fix client session

@sio.on('disconnect')
async def disconnect(sid):
    global sio_client_count
    sio_client_count -= 1
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")

@sio.on('fixme-client')
async def fixme_client(sid, order_data):
    print(f"\tW.Socket client [{sid}] sent ob order: {order_data}")
    app = await client_app
    await app.submit_order(order_data)

# @sio.on('fixme-dealer')
# async def fixme_dealer(sid, axe_data):
#     print(f"\tW.Socket client [{sid}] sent axe to upload: {axe_data}")
#     app = await dealer_app
#     await app.submit_order(axe_data)
