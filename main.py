import asyncio
from collector import start_collector
from admin_bot import start_admin_bot

async def main():
    await asyncio.gather(
        start_collector(),
        start_admin_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())