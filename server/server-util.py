import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

os.environ["SERVER_MODE"] = "util"
import instances
from src.fastapi import router as fastapi_router

fixme = os.environ.get("FIXME_MODE", "")
fixme_server_port = int(os.environ.get("FIXME_SERVER_PORT", ""))
notification_server_port = int(os.environ.get("NOTIFICATION_SERVER_PORT", ""))
util_server_port = fixme_server_port if fixme == "true" else notification_server_port

fastapi_app = instances.fastapi_app
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.include_router(fastapi_router)

if __name__ == "__main__":
    uvicorn.run(
        "server-util:fastapi_app",
        host="0.0.0.0",
        port=util_server_port,
        lifespan="on",
    )
