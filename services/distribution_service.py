import logging
import time
import datetime
import asyncio

from config import TOKEN
from config import BIRTHDAY_NOTIFICATION_DAY_OFFSET
from config import BIRTHDAY_TSTAMP_FORMAT, REMINDER_TSTAMP_FORMAT

from database.controllers.employee_controller import EmployeeController
from database.controllers.subscriber_controller import SubscriberController
from services.translation_service import TranslationService as TS

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

locale_ru = TS.getTranslation("ru")


class DistributionService:

    year_seconds = 31556952
    day_seconds = 86400
    hour_seconds = 3600
    minute_seconds = 60
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # TODO: find out what this function actually returns
    # (God I hate Python)
    @classmethod
    def calculateNotificaionTime(cls, birth_date, reminder_day_offset) -> int:
        """
        Calculates the time of the next notification.

        birth_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        current_year = time.localtime().tm_year - 1970
        stripped_reminder_date = (birth_date - reminder_day_offset * cls.day_seconds) % cls.year_seconds
        stripped_date_now = time.time() % cls.year_seconds

        # If current stripped day is > stripped reminder date, then add 1 year
        extra_years = 1 if stripped_reminder_date < stripped_date_now else 0

        return (current_year + extra_years) * cls.year_seconds + stripped_reminder_date

    @classmethod
    def currentTimeFitsPeriod(cls, date, day_offset) -> bool:
        """
        Checks if the current time is in the given period.

        date - The target date
        day_offset - Offset in days from the date.
        """
        current_year = (time.localtime().tm_year - 1970) * cls.year_seconds
        stripped_date = date % cls.year_seconds + current_year
        return (stripped_date - day_offset * cls.day_seconds) < time.time() and time.time() < stripped_date

    @classmethod
    def isNotificationDue(cls, target_date, reminder_day_offset) -> int:
        """
        Checks if the notification is due.
        Returns -1 if late, 1 if on time, 0 if early

        target_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        current_time = time.time()
        if current_time > target_date + (reminder_day_offset * cls.day_seconds):
            return -1  # Late
        elif current_time > target_date:
            return 1  # On time
        else:
            return 0  # Early

    def timestampToUnix(timestamp, format) -> int:
        """
        Converts a timestamp sring in the given format
        to unix timestamp (integer).

        timestamp - timestamp string
        format - timestamp format
        """
        return int(datetime.datetime.strptime(timestamp, format).timestamp())

    def unixToTimestamp(unix, format) -> str:
        """
        Converts a unix timestamp (integer)
        to a timestamp string in the given format.

        unix - unix timestamp
        format - timestamp format
        """
        return datetime.datetime.fromtimestamp(unix).strftime(format)

    @classmethod
    async def handleEmployeeSchedule(cls, employee) -> bool:
        """
        Sends a notification to the employee if time is due
        and schedules the next notification.
        Returns true if the notification was sent.

        employee - must be an Employee object
        """
        birthday_timestamp = cls.timestampToUnix(employee.birthday, BIRTHDAY_TSTAMP_FORMAT)

        # Generated but will not necessarily be used
        new_scheduled_reminder = cls.calculateNotificaionTime(birthday_timestamp, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Employee has no reminder scheduled, let's fix it
        if employee.scheduled_reminder is None:

            # Sometimes an employee's birthday is inside the notification
            # period when the reminder is not yet scheduled, resulting
            # in a reminder being scheduled for the next year. That's why
            # we need to intervene and send the notification right away.
            if cls.currentTimeFitsPeriod(birthday_timestamp, BIRTHDAY_NOTIFICATION_DAY_OFFSET):
                await cls.broadcastBirthdayNotification(employee)

            employee.scheduled_reminder = cls.unixToTimestamp(new_scheduled_reminder, REMINDER_TSTAMP_FORMAT)
            employee.save()
            logger.info(f"{employee.full_name} ({employee.tg_id}) - scheduled for {employee.scheduled_reminder}")

            return False

        # Checking scheduled notification time to see if we should do anything
        scheduled_reminder_unix = cls.timestampToUnix(employee.scheduled_reminder, REMINDER_TSTAMP_FORMAT)
        due_state = cls.isNotificationDue(scheduled_reminder_unix, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Too early, nothing to do
        if due_state == 0:
            logger.info(f"{employee.full_name} ({employee.tg_id}) - nothing to do")
            return False

        # Time to send the notification
        if due_state == 1:
            await cls.broadcastBirthdayNotification(employee)

        # We either got it in time or too late,
        # let's schedule the next notification
        employee.scheduled_reminder = cls.unixToTimestamp(new_scheduled_reminder, REMINDER_TSTAMP_FORMAT)
        employee.save()

        logger.info(f"{employee.full_name} ({employee.tg_id}) - reminder set to {employee.scheduled_reminder}")

        return False

    @classmethod
    async def handleEmployeeScheduleById(cls, id) -> bool:
        """
        Wrapper of employeeBirthdayNotification to be
        used with the id of the employee.

        id - id of Employee.
        """
        employee = await EmployeeController.getEmployeeById(id)
        return await cls.handleEmployeeSchedule(employee)

    @classmethod
    async def broadcastBirthdayNotification(cls, employee) -> bool:
        """
        Sends notifications to all subscribers.
        Returns true if the notification was sent.

        employee - must be an Employee object
        """
        # Gathers subscribers to be able to notify them
        subscribers = await SubscriberController.getSubscribedUsers()

        logger.info(f"{employee.full_name} ({employee.tg_id}) - broadcasting notification...")

        template = TS.getTemplate(locale_ru, "birthdayNotification")
        message_text = template.format(
            employee=employee.full_name,
            date=employee.birthday
        )

        # List of task to be run in parallel
        tasks = [
            cls.bot.send_message(
                chat_id=subscriber.tg_id,
                text=message_text)
            for subscriber in subscribers
        ]

        # Running the tasks
        await asyncio.gather(*tasks)
        logger.info(f"{employee.full_name} ({employee.tg_id}) - finished broadcasting.")

        return True

    @classmethod
    async def birthdayCycle(cls, forever=False, interval=hour_seconds) -> None:
        """
        Handles birthday notifications at fixed periods of time.
        """

        # Avoid overloading
        if interval is None or interval < cls.minute_seconds:
            raise ValueError("Cycle interval must be at least 1 minute.")

        while True:
            for employee in await EmployeeController.getEmployees():
                try:
                    await cls.handleEmployeeSchedule(employee)
                except Exception as e:
                    logger.exception(f"Failed to send birthday notification: {e}")

            if not forever:
                break

            await asyncio.sleep(interval)
