from sys import exit

from os import getenv
from dotenv import load_dotenv

load_dotenv(override=False)

"""
Configuration file for the bot.

Utilizes environment variables and makes them accessible
everywhere else.

Do not modify this file, configure variables in your
environment instead.
"""


# BOT_TOKEN - Your Telegram bot token (Avaiable from @BotFather)
#    (Example: 1234567890:ABCDefghijk)
TOKEN = getenv("BOT_TOKEN") or exit("BOT_TOKEN not found in environment!")

# DATABASE - Your SQLite database path.
#    (Default: database.db)
DATABASE = getenv("DATABASE") or "database.db"

# ADMINS - List of admin Telegram IDs with complete access.
#    (Example: 1234567890,1234567891,1234567892)
ADMINS = list((getenv("ADMINS") or "").split(","))
