import asyncio
import sys
import socketio
import config
from src.util.executor import create_command
from src.component.card.remote import total_s3_objects

sys.path.append("./src")
from config import (
    node_env,
    redis,
    the_lab_log_file_name,
    the_lab_log_file_path,
)
from util.streamer import start_streaming_log_file, stop_streaming_log_file
from util.executor import run_a_command_on_local

sio_client_count = 0
global_total_s3_objects = 0

sio: socketio.AsyncServer = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")
config.sio = sio
config.socketio_app = socketio_app


async def update_total_s3_objects():
    global global_total_s3_objects

    while True:
        current_total_s3_objects = total_s3_objects()
        await asyncio.sleep(10)
        if current_total_s3_objects > global_total_s3_objects:
            await sio.emit("alert", {"new_alert": True})
            global_total_s3_objects = current_total_s3_objects

            cards_app = config.fastapi_app.state.cards_app
            await cards_app.fetch_cards_from_source_and_cache({"environment": "qa", "day": 1, "source": "remote"})  # update cards in app state
            await cards_app.fetch_cards_from_source_and_cache({"environment": "qa", "day": 1, "source": "local"})  # update cards in app state
            # await cards_app.set_cards({"environment": "qa", "day": 1, "source": "remote"}) # update cards in app state


@sio.on("connect") # type: ignore
async def connect(sid, environ):
    global sio_client_count
    sio_client_count += 1

    print(f"\tConnected to W.S. client... [{sid}] | Connection #{sio_client_count}")
    await sio.emit(
        "message",
        f"FASTAPI W.S. server connected! #{sio_client_count} | Node Env: {node_env}",
        room=sid,
    )
    if node_env == "production":
        asyncio.create_task(redis.update_redis_cache_client_data(sio_client_count))
        asyncio.create_task(update_total_s3_objects())


@sio.on("disconnect") # type: ignore
async def disconnect(sid):
    global sio_client_count
    sio_client_count -= 1
    await stop_streaming_log_file(sid)
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")


@sio.on("cards") # type: ignore
async def cards(sid, expected_filter_data: dict):
    print(f"Socket client [{sid}] sent data to cards: {expected_filter_data}")
    cards_app = config.fastapi_app.state.cards_app
    if cards_app:
        cards = await cards_app.get_cards_from_cache(expected_filter_data)
        print(f"Cards total in app state: {len(cards)}")
        if len(cards) == 0:
            print("No cards found in app state.")
            await sio.emit("cards", False, room=sid)
            return
        for card in cards:
            await sio.emit("cards", card, room=sid)
    else:
        print("Cards class not found in app state.")
        await sio.emit("cards", False, room=sid)
        return


@sio.on("fixme") # type: ignore
async def fixme_client(sid, order):
    print(f"Socket client [{sid}] sent data to fixme: {order}")
    if not config.fastapi_app:
        print("FastAPI app not set in config.")
        return

    # Grab fix_client_app from app.state
    fix_client_app = await config.fastapi_app.state.fix_client_task
    if not fix_client_app:
        print("fix_client_app not found on app.state.")
        return

    fix_client_app.submitOrder(order, {}, {})


@sio.on("the-lab") # type: ignore
async def the_lab(sid, options):
    """Run a command using The Lab to execute the playwright test suite"""
    print(f"SIO received command: {options} | type {type(options)}")

    subscription = "the-lab"
    command = create_command(options)
    command_task = asyncio.create_task(
        run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")
    )  # start background task to run the command

    await start_streaming_log_file(
        sio, sid, subscription, the_lab_log_file_path
    )  # start background task to stream the log file
    await command_task
