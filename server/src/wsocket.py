import platform
import sys
import asyncio
import socketio
import config
from src.component.local import get_all_local_cards
from src.component.remote import get_all_s3_cards, total_s3_objects

sys.path.append("./src")
from config import the_lab_log_file_path, the_lab_log_file_name, local_dir
from util.streamer import start_streaming_log_file, stop_streaming_log_file
from util.executor import run_a_command_on_local

sio_client_count = 0
global_total_s3_objects = 0

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socketio_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io")
config.sio = sio
config.socketio_app = socketio_app


async def update_total_s3_objects():
    retry = 0
    global global_total_s3_objects
    while retry < 300:
        current_total_s3_objects = total_s3_objects()
        await asyncio.sleep(1)
        print(f" current_total_s3_objects: {current_total_s3_objects}... Retrying# {retry}")
        retry += 1
        if current_total_s3_objects > global_total_s3_objects:
            await sio.emit("alert", {"new_alert": True})
            global_total_s3_objects = current_total_s3_objects


@sio.on("connect")
async def connect(sid, environ):
    global sio_client_count
    sio_client_count += 1
    print(f"\tConnected to client... [{sid}] | Clients connected: {sio_client_count}")
    await sio.emit(
        "message",
        f"Hello from the FASTAPI W.S. server! | Clients connected: {sio_client_count}",
        room=sid,
    )
    asyncio.create_task(update_total_s3_objects())


@sio.on("disconnect")
async def disconnect(sid):
    global sio_client_count
    sio_client_count -= 1
    await stop_streaming_log_file(sid)
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")


@sio.on("cards")
async def cards(sid, filter: dict):
    print(f"Socket client [{sid}] sent data to cards: {filter}")
    source = filter.get("source")
    environment = filter.get("environment")
    day = int(filter.get("day"))
    print(f"Report Source: {source} | Filter: {day} | Environment: {environment}")
    cards = []
    if source == "remote":
        cards = get_all_s3_cards(sio, sid, filter)
    else:
        cards = get_all_local_cards(sio, sid, day)
    await cards


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

    await fix_client_app.submitOrder(order, {}, {})


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
