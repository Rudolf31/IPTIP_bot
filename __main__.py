import logging
import sys
import asyncio

from services.bot_service import run_bot
from services.distribution_service import DistributionService
from database.application_context import AppContext

ctx = None

def main() -> None:

    global ctx
    ctx = AppContext()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(DistributionService.birthdayCycle(forever=True, interval=600))
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
