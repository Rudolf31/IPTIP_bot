import logging
import sys
import asyncio

from services.bot_service import run_bot


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
