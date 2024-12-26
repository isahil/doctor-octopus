import asyncio
import socketio
from .fix_client import FixClient

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

sio = socketio.AsyncServer(cors_allowed_origins=origins,async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")

fix_client = FixClient(env="qa", app="fix", fix_side="client", timeout=60, broadcast=True, sio=sio)

fix_dealer = FixClient(env="qa", app="fix", fix_side="dealer", timeout=30, broadcast=True, sio=sio)

__all__ = ["socketio_app", "sio", "fix_client"]

client_count = 0
client_apps = {}

@sio.on('connect')
async def connect(sid, environ):
    global client_count
    client_count += 1
    print(f"\tConnected to client... [{sid}] | Clients connected: {client_count}")
    await sio.emit('message', f'Hello from the FASTAPI W.S. server! | Clients connected: {client_count}', room=sid)
    client_app = sio.start_background_task(fix_client.start_client) # start background task to connect to the fix client session
    client_apps[sid] = client_app

@sio.on('disconnect')
async def disconnect(sid):
    global client_count
    client_count -= 1
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {client_count}")

@sio.on('fixme-client')
async def fixme_client(sid, order_data):
    print(f"\tW.Socket client [{sid}] sent ob order: {order_data}")
    # add steps to process/send order to the fix client session
    if sid in client_apps:
        print(f"\tClient app found for socket client [{sid}]")
        client_app = await client_apps[sid]
        await client_app.submit_order(order_data)
    else:
        print(f"\tNo client app found for socket client [{sid}]")

@sio.on('fixme-dealer')
async def fixme_dealer(sid, axe_data):
    print(f"\tW.Socket client [{sid}] sent axe to upload: {axe_data}")
    # add steps to process/send axe to the fix dealer session
    # await fix_dealer.submit_order(axe_data)