import asyncio
from fastapi import FastAPI
from socketio import AsyncServer
from src.utils.env_loader import get_node_env
from src.utils.streamer import start_streaming_log_file, stop_streaming_log_file
from src.utils.logger import logger
from src.utils.executor import create_command, run_a_command_on_local
from config import the_lab_log_file_name, do_current_clients_count_key


class WebSocketServer:
    import instances

    sio: AsyncServer
    fastapi_app: FastAPI

    def __init__(self, sio: AsyncServer, fastapi_app: FastAPI):
        self.sio = sio
        self.fastapi_app = fastapi_app
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("cards", self.cards)
        self.sio.on("fixme", self.fixme_client)
        self.sio.on("the-lab", self.the_lab)
        logger.info(f"WebSocketServer initialized with SIO: {sio is not None}")

    async def connect(self, sid, environ, auth=None, namespace="/"):
        do_clients_count = self.instances.redis.get(do_current_clients_count_key)
        node_env = get_node_env()

        logger.info(f"\tConnected to W.S. client... [{sid}] | Connection #{do_clients_count}")
        await self.sio.emit(
            "message",
            f"FASTAPI W.S. server connected! #{do_clients_count} | Node Env: {node_env}",
            room=sid,
        )
        if node_env == "production":
            self.instances.redis.refresh_redis_client_metrics()
            await self.sio.emit(
                "message",
                f"DO active clients count: {do_clients_count} | Node Env: {node_env}",
                room=sid,
            )

    async def disconnect(self, sid, namespace="/"):
        do_clients_count = self.instances.redis.decrement_key(do_current_clients_count_key)
        await stop_streaming_log_file(sid)
        logger.info(f"\tDisconnected from socket client... [{sid}] | Clients connected: {do_clients_count}")

    async def cards(self, sid, expected_filter_data: dict, namespace="/"):
        logger.info(f"Socket client [{sid}] sent data to cards: {expected_filter_data}")
        cards = self.fastapi_app.state.cards
        if cards:
            cards = cards.get_cards_from_cache(expected_filter_data)
            if len(cards) == 0:
                logger.info(f"No cards found in cache. length: {len(cards)}")
                await self.sio.emit("cards", False, room=sid)
                return

            for card in cards:
                await self.sio.emit("cards", card, room=sid)
        else:
            logger.info("Cards class not found in app state.")
            await self.sio.emit("cards", False, room=sid)

    async def fixme_client(self, sid, order, namespace="/"):
        logger.info(f"Socket client [{sid}] sent data to fixme: {order}")
        fix = await self.fastapi_app.state.fix
        if not fix:
            logger.info("fix instance not found in fastapi_app.state")
            return
        fix.submitOrder(order, {}, {})

    async def the_lab(self, sid, options, namespace="/"):
        """Run a command using The Lab to execute the playwright test suite"""
        logger.info(f"SIO received command: {options} | type {type(options)}")

        subscription = "the-lab"
        command = create_command(options)
        command_task = asyncio.create_task(
            run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")
        )  # start background task to run the command
        the_lab_log_file_path: str = self.fastapi_app.state.the_lab_log_file_path

        await start_streaming_log_file(self.sio, sid, subscription, the_lab_log_file_path)
        await command_task
