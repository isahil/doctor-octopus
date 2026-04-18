from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

import src.services.notification as notification
from src.utils.logger import logger


router = APIRouter()


@router.get("/notifications/{client_id}", response_class=StreamingResponse)
async def notifications_sse(client_id: str, request: Request) -> StreamingResponse:
    logger.info(f"Client [{client_id}] connected to /notifications S.S.E endpoint")
    return StreamingResponse(
        notification.notification_streamer(request, client_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
