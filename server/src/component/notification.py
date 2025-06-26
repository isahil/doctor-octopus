import asyncio
# import os
# import sys

# Add the server directory to the path when run standalone
# script_dir = os.path.dirname(os.path.abspath(__file__))
# server_dir = os.path.abspath(os.path.join(script_dir, "../.."))
# sys.path.insert(0, server_dir)

import instances # noqa
from config import notification_frequency_time # noqa
from src.component.remote import total_s3_objects # noqa
from src.util.logger import logger # noqa


async def update_alert_total_s3_objects():
    """Update the total number of S3 objects and emit an alert if the count increases"""
    try:
        sio = instances.sio
        cards = instances.fastapi_app.state.cards if hasattr(instances.fastapi_app, "state") else None
        initial_total_s3_objects = total_s3_objects()
        logger.info(f"S3 TOTAL: {initial_total_s3_objects}")

        await asyncio.sleep(notification_frequency_time)

        while True:
            current_total_s3_objects = total_s3_objects()
            # subprocess.run(["sh", "./echo.sh"])
            if current_total_s3_objects > initial_total_s3_objects:
                logger.info(f"new alert: {current_total_s3_objects}")
                if sio:
                    await sio.emit("alert", {"new_alert": True})
                initial_total_s3_objects = current_total_s3_objects

                if cards:
                    await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "remote"})
                    await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "local"})
                
                await asyncio.sleep(notification_frequency_time)
    except Exception as e:
        logger.error(f"Error in notification service: {str(e)}")
        raise


if __name__ == "__main__":
    logger.info("Starting the S3 update notification task...")
    asyncio.run(update_alert_total_s3_objects())
