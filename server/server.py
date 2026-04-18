# This is the entry point of the main server process
import os
from fastapi import FastAPI
from src.utils.lifespan import lifespan_main
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from config import workers_limit
from src.utils.env_loader import get_debug_mode, get_main_server_port, get_node_env
from src.fast_router import router

debug = get_debug_mode()

fastapi_app: FastAPI = FastAPI(lifespan=lifespan_main, debug=True if debug == "true" else False)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.add_middleware(GZipMiddleware, minimum_size=1000)
fastapi_app.include_router(router)
fastapi_app.mount("/test_reports", StaticFiles(directory="./test_reports"), name="Test Reports")

if __name__ == "__main__":
    main_server_port = get_main_server_port()
    node_env = get_node_env()

    uvicorn.run(
        "server:fastapi_app",
        host="0.0.0.0",
        port=main_server_port,
        lifespan="on",
        workers=workers_limit,
        forwarded_allow_ips="*",
        reload=(node_env != "production"),
    )

# "author": "Imran Sahil"
# "GitHub": "https://github.com/isahil/doctor-octopus.git"
# "description": "A test runner & report viewer application using FastAPI and SocketIO for the server and React for the client."
