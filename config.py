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

# SYSTEM AND ADMINISTRATION

# BOT_TOKEN - Your Telegram bot token (Avaiable from @BotFather)
#    (Example: 1234567890:ABCDefghijk)
TOKEN = getenv("BOT_TOKEN") or exit("BOT_TOKEN not found in environment!")

# DATABASE - Your SQLite database path.
#    (Default: database.db)
DATABASE = getenv("DATABASE") or "database.db"

# ADMINS - List of admin Telegram IDs with complete access.
#    (Example: 1234567890,1234567891,1234567892)
ADMINS = list((getenv("ADMINS") or "").split(","))

# CUSTOMIZATION

# TIMEZONE - Your timezone.
#    (Default: Europe/Moscow)
TIMEZONE = getenv("TIMEZONE") or "Europe/Moscow"

# BIRTHDAY_TSTAMP_FORMAT - Format of the birthday timestamp.
# Used to store employees' birthdays.
#    (Default: %d-%m-%Y)
BIRTHDAY_TSTAMP_FORMAT = getenv("BIRTHDAY_TSTAMP_FORMAT") or "%d-%m-%Y"

# REMINDER_TSTAMP_FORMAT - Format of the reminder timestamp.
# Used to store employees' birthday notifications and reminders.
#    (Default: %d-%m-%Y %H:%M:%S)
REMINDER_TSTAMP_FORMAT = getenv("REMINDER_TSTAMP_FORMAT") or "%d-%m-%Y %H:%M:%S"

# BIRTHDAY_NOTIFICATION_DAY_OFFSET - Offset in days for birthday reminder.
# Notifications for the birthday will be sent N days before it happens.
#    (Default: 3)
BIRTHDAY_NOTIFICATION_DAY_OFFSET = getenv("BIRTHDAY_NOTIFICATION_DAY_OFFSET") or 3

# DEVELOPMENT

# ENVIRONMENT - Type of environment (production/debug)
#    (Default: production)
ENVIRONMENT = getenv("ENVIRONMENT") or "production"
