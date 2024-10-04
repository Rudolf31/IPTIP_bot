import logging
import sys
import asyncio

from services.bot_service import run_bot
from services.distribution_service import DistributionService


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(DistributionService.birthdayCycle())
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
