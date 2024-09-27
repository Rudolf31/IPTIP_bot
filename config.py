from os import getenv

"""
Configuration file for the bot.

Utilizes environment variables and makes them accessible
everywhere else.

Do not modify this file, configure variables in your
environment instead.
"""


# BOT_TOKEN - Your Telegram bot token (Avaiable from @BotFather)
TOKEN = getenv("BOT_TOKEN")

# DATABASE - Your SQLite database path.
DATABASE = getenv("DATABASE")
