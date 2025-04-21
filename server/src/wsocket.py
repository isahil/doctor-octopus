import asyncio
import config
import platform
import sys
import socketio
from src.component.card.remote import total_s3_objects

sys.path.append("./src")
from config import (
    lifetime_doctor_clients_count_key,
    local_dir,
    max_concurrent_clients_key,
    node_env,
    the_lab_log_file_name,
    the_lab_log_file_path,
)
from util.streamer import start_streaming_log_file, stop_streaming_log_file
from util.executor import run_a_command_on_local
from util.redis import RedisClient

sio_client_count = 0
global_total_s3_objects = 0

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
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
            cards_app.set_cards({"environment": "qa", "day": 1}) # update cards in app state


def update_redis_cache_client_data():
    global sio_client_count

    redis = RedisClient()
    redis.redis_client.incr(lifetime_doctor_clients_count_key, 1)

    try:
        max_concurrent_clients = int(redis.redis_client.get(max_concurrent_clients_key).decode("utf-8"))
        if sio_client_count > max_concurrent_clients:
            redis.redis_client.set(max_concurrent_clients_key, sio_client_count)
    except Exception as _:
        redis.redis_client.incr(max_concurrent_clients_key, 1)


@sio.on("connect")
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
        update_redis_cache_client_data()
    asyncio.create_task(update_total_s3_objects())


@sio.on("disconnect")
async def disconnect(sid):
    global sio_client_count
    sio_client_count -= 1
    await stop_streaming_log_file(sid)
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")


@sio.on("cards")
async def cards(sid, expected_filter_data: dict):
    print(f"Socket client [{sid}] sent data to cards: {expected_filter_data}")
    cards_app = config.fastapi_app.state.cards_app
    if cards_app:
        cards = cards_app.get_cards(expected_filter_data)
        # print(f"Cards total in app state: {len(cards)}")
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


@sio.on("fixme")
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


@sio.on("the-lab")
async def the_lab(sid, command):
    """Run a command using The Lab to execute the playwright test suite"""
    print(f"SIO received command: {command} | type {type(command)}")
    lab_options = command
    env = lab_options.get("environment")
    app = lab_options.get("app")
    proto = lab_options.get("proto")
    suite = lab_options.get("suite")
    subscription = "the-lab"

    os = platform.system().lower()
    if os == "darwin" or os == "linux":
        command = f"cd {local_dir} && ENVIRONMENT={env} APP={app} npm test {proto}:{suite}"
    elif os == "windows":
        command = f"cd {local_dir} && set ENVIRONMENT={env}& set APP={app}& npm test {proto}:{suite}"
    else:
        raise OSError("Unsupported OS to run command")
    command_task = asyncio.create_task(
        run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")
    )  # start background task to run the command

    await start_streaming_log_file(
        sio, sid, subscription, the_lab_log_file_path
    )  # start background task to stream the log file
    await command_task  # wait for the command task to finish
