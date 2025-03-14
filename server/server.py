# This is the entry point of the server application
import config
import os
import sys  # noqa
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import the_lab_log_file_path, server_mode
from src.wsocket import sio, socketio_app
from src.fastapi import router as fastapi_router
from src.util.fix_client import FixClient
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fix/')))
# from fix_client_async import FixClient # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI server.
    Steps before yield gets executed before the server starts.
    Steps after yield gets executed after the server shuts down
    """
    print("Starting the server lifespan...")
    if os.path.exists(the_lab_log_file_path):
        with open(the_lab_log_file_path, "w"):
            pass

    try:
        print("Starting the server lifespan...")
        # Initialize your tasks
        if server_mode == "fixme":
            fix_client = FixClient(
                {"environment": "uat", "app": "loan", "fix_side": "client", "counter": "1", "sio": sio}
            )
            fix_client_task = asyncio.create_task(fix_client.start_mock_client())
            app.state.fix_client = fix_client
            app.state.fix_client_task = fix_client_task

        yield

    except asyncio.CancelledError:
        print("Received shutdown signal, cleaning up...")
        raise

    finally:
        print("Shutting down the server lifespan...")
        if server_mode == "fixme":
            # Cancel the task and wait for it to complete
            if hasattr(app.state, "fix_client_task"):
                fix_client_task = app.state.fix_client_task
                fix_client_task.cancel()
                try:
                    await asyncio.wait_for(fix_client_task, timeout=5.0)
                except asyncio.TimeoutError:
                    print("Timeout waiting for fix_client_task to cancel")
                except asyncio.CancelledError:
                    print("fix_client_task cancelled successfully")
                except Exception as e:
                    print(f"Error during fix_client_task cleanup: {e}")


fastapi_app = FastAPI(lifespan=lifespan)
config.fastapi_app = fastapi_app

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(fastapi_router)
fastapi_app.mount("/ws/socket.io", socketio_app)

if __name__ == "__main__":
    uvicorn.run(socketio_app, host="0.0.0.0", port=8000, lifespan="on", reload=True)

# "author": "Imran Sahil"
# "github": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
