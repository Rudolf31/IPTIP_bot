import logging
import sys
import asyncio

from services.bot_service import run_bot
from services.distribution_service import DistributionService
from database.application_context import AppContext


async def main() -> None:

    async with AppContext():
        pass

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await asyncio.gather(
        run_bot(),
        DistributionService.birthdayCycle(forever=True, interval=600)
    )


if __name__ == "__main__":
    asyncio.run(main())
