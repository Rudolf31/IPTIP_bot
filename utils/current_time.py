import pendulum

from config import TIMEZONE


def now():
    return pendulum.now(TIMEZONE)