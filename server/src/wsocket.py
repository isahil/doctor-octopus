import asyncio
import sys
from socketio import AsyncServer

import instances
sys.path.append("./src")
from config import (
    node_env,
    the_lab_log_file_name,
    the_lab_log_file_path,
    current_doctor_clients_count_key
)
from util.streamer import start_streaming_log_file, stop_streaming_log_file
from util.logger import logger
from src.util.executor import create_command, run_a_command_on_local
sio: AsyncServer = instances.sio
logger.info(f"sio initialized: {sio is not None} | type: {type(sio)}")

@sio.on("connect")  # type: ignore
async def connect(sid, _):
    sio_client_count = await instances.fastapi_app.state.redis_client.get(current_doctor_clients_count_key)

    logger.info(f"\tConnected to W.S. client... [{sid}] | Connection #{sio_client_count}")
    await sio.emit(
        "message",
        f"FASTAPI W.S. server connected! #{sio_client_count} | Node Env: {node_env}",
        room=sid,
    )
    if node_env == "production":
        count = await instances.fastapi_app.state.redis.update_redis_cache_client_data()
        logger.info(f"Redis cache updated with client data. Total clients: {count}")
        await sio.emit(
            "message",
            f"Total clients: {count} #{sio_client_count} | Node Env: {node_env}",
            room=sid,
        )


@sio.on("disconnect")  # type: ignore
async def disconnect(sid):
    sio_client_count = await instances.fastapi_app.state.redis.decrement_key(current_doctor_clients_count_key)
    await stop_streaming_log_file(sid)
    logger.info(f"\tDisconnected from socket client... [{sid}] | Clients connected: {sio_client_count}")


@sio.on("cards")  # type: ignore
async def cards(sid, expected_filter_data: dict):
    logger.info(f"Socket client [{sid}] sent data to cards: {expected_filter_data}")
    cards = instances.fastapi_app.state.cards
    if cards:
        cards = await cards.get_cards_from_cache(expected_filter_data)
        if len(cards) == 0:
            logger.info(f"No cards found in cache. length: {len(cards)}")
            await sio.emit("cards", False, room=sid)
            return

        for card in cards:
            await sio.emit("cards", card, room=sid)
    else:
        logger.info("Cards class not found in app state.")
        await sio.emit("cards", False, room=sid)


@sio.on("fixme")  # type: ignore
async def fixme_client(sid, order):
    logger.info(f"Socket client [{sid}] sent data to fixme: {order}")
    fix = await instances.fastapi_app.state.fix
    if not fix:
        logger.info("fix instance not found in fastapi_app.state")
        return
    fix.submitOrder(order, {}, {})


@sio.on("the-lab")  # type: ignore
async def the_lab(sid, options):
    """Run a command using The Lab to execute the playwright test suite"""
    logger.info(f"SIO received command: {options} | type {type(options)}")

    subscription = "the-lab"
    command = create_command(options)
    command_task = asyncio.create_task(
        run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")
    )  # start background task to run the command

    await start_streaming_log_file(sio, sid, subscription, the_lab_log_file_path)
    await command_task
