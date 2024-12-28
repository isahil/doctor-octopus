import sys
import asyncio
import socketio
sys.path.append("./src")
from fix_client import FixClient

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

sio = socketio.AsyncServer(cors_allowed_origins=origins,async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")

fix_client = FixClient(env="qa", app="fix", fix_side="client", broadcast=True, sio=sio)
client_app = asyncio.create_task(fix_client.start_mock_client())

# fix_dealer = FixClient(env="qa", app="fix", fix_side="dealer", broadcast=True, sio=sio)
# dealer_app = asyncio.create_task(fix_dealer.start_mock_client())

__all__ = ["socketio_app", "sio", "fix_client"]

sio_client_count = 0

@sio.on('connect')
async def connect(sid, environ):
    global sio_client_count
    sio_client_count += 1
    print(f"\tConnected to client... [{sid}] | Clients connected: {sio_client_count}")
    await sio.emit('message', f'Hello from the FASTAPI W.S. server! | Clients connected: {sio_client_count}', room=sid)
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
