import platform
import sys
import asyncio
from ..server import fastapi_app, sio
sys.path.append("./src")
from config import the_lab_log_file_path, the_lab_log_file_name, local_dir
from util.streamer import start_streaming_log_file, stop_streaming_log_file
from util.executor import run_a_command_on_local

sio_client_count = 0

@sio.on('connect')
async def connect(sid, environ):
    global sio_client_count
    sio_client_count += 1
    print(f"\tConnected to client... [{sid}] | Clients connected: {sio_client_count}")
    await sio.emit('message', f'Hello from the FASTAPI W.S. server! | Clients connected: {sio_client_count}', room=sid)

@sio.on('disconnect')
async def disconnect(sid):
    global sio_client_count
    sio_client_count -= 1
    await stop_streaming_log_file(sid)
    print(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")

@sio.on('fixme')
async def fixme_client(sid, fix_side, order_data):
    print(f"\tW.Socket client [{sid}] sent data to {fix_side} side fix: {order_data}")
    
    # await sio.emit(f'fixme-{fix_side}', "FixMe app is not runnable yet", room=sid)
    app = await eval(f"{fastapi_app}.state.fix_{fix_side}_app")
    await app.submit_order(order_data)

@sio.on('the-lab')
async def the_lab(sid, command):
    ''' Run a command using The Lab to execute the playwright test suite '''
    print(f"SIO received command: {command} | type {type(command)}")
    lab_options = command
    env = lab_options.get("environment")
    app = lab_options.get("app")
    proto = lab_options.get("proto")
    suite = lab_options.get("suite")
    subscription = 'the-lab-log'

    os = platform.system().lower()
    if os == "darwin" or os == "linux":
        command = f"cd {local_dir} && ENVIRONMENT={env} APP={app} npm run {proto}:{suite}"
    elif os == "windows": command = f"cd {local_dir} && set ENVIRONMENT={env}& set APP={app}& npm run {proto}:{suite}"
    else : raise OSError("Unsupported OS to run command")
    command_task = asyncio.create_task(run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")) # start background task to run the command
    
    await start_streaming_log_file(sio, sid, subscription, the_lab_log_file_path) # start background task to stream the log file
    await command_task # wait for the command to finish

