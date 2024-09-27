from services.bot_service import run_bot
import logging
import sys
import asyncio
from database.application_context import AppContext

async def test():
    async with AppContext() as database:
        pass

def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(test())
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()