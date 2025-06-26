import asyncio
import instances
from config import notification_frequency_time
from src.component.remote import total_s3_objects
from src.util.logger import logger

async def update_alert_total_s3_objects():
    '''Update the total number of S3 objects and emit an alert if the count increases'''
    sio = instances.sio
    cards = instances.fastapi_app.state.cards
    global_total_s3_objects = total_s3_objects()
    logger.info(f"S3 TOTAL: {global_total_s3_objects}")

    await asyncio.sleep(notification_frequency_time)

    while True:
        current_total_s3_objects = total_s3_objects()
        # subprocess.run(["sh", "./echo.sh"])
        if current_total_s3_objects > global_total_s3_objects:
            logger.info(f"new alert: {current_total_s3_objects}")
            await sio.emit("alert", {"new_alert": True})
            global_total_s3_objects = current_total_s3_objects

            await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "remote"})
            await cards.fetch_cards_and_cache({"environment": "qa", "day": 1, "source": "local"})
            # await cards.set_cards({"environment": "qa", "day": 1, "source": "remote"}) # update cards in app state
            await asyncio.sleep(notification_frequency_time)


if __name__ == "__main__":
    print("Starting the S3 objects update notification task...")
    asyncio.run(update_alert_total_s3_objects())
