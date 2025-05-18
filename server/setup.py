import asyncio
import os
import platform
from src.component.card.cards import Cards


async def main():
    os_name = platform.system()
    print(os_name)

    if os_name == "Windows":
        os.environ["OS_NAME"] = "Windows"
    elif os_name == "Darwin":
        os.environ["OS_NAME"] = "Mac"
    elif os_name == "Linux":
        os.environ["OS_NAME"] = "Linux"
    else:
        print("Unknown OS")

    # subprocess.run(["sh", "./start.sh"])
    cards = Cards()
    await cards.fetch_cards_from_source_and_cache({"environment": "qa", "day": 1, "source": "remote"})


if __name__ == "__main__":
    asyncio.run(main())
