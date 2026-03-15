import asyncio
from fastapi import FastAPI
from socketio import AsyncServer
from config import the_lab_log_file_name
from src.utils.logger import logger
from src.utils.streamer import start_streaming_log_file, stop_streaming_log_file
from src.utils.executor import create_command, run_a_command_on_local

class WebSocketServer:
    sio: AsyncServer
    fastapi_app: FastAPI

    def __init__(self, sio: AsyncServer, fastapi_app: FastAPI):
        self.sio = sio
        self.fastapi_app = fastapi_app
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("fixme", self.fixme_client)
        self.sio.on("the-lab", self.the_lab)
        logger.info(f"WebSocketServer initialized with SIO: {sio is not None}")

    async def connect(self, sid, environ, auth=None, namespace="/"):
        logger.info(f"\tConnected to W.S. client... [{sid}]")
        await self.sio.emit(
            "message",
            f"FIXME W.S. server connected!",
            room=sid,
        )

    async def disconnect(self, sid, namespace="/"):
        await stop_streaming_log_file(sid)
        logger.info(f"\tDisconnected from socket client... [{sid}]")

    async def fixme_client(self, sid, order, namespace="/"):
        logger.info(f"Socket client [{sid}] sent data to fixme: {order}")
        fix = self.fastapi_app.state.fix
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
