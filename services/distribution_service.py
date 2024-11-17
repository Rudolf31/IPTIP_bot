import logging
import time
import datetime
import asyncio
import pendulum

from config import TOKEN
from config import BIRTHDAY_NOTIFICATION_DAY_OFFSET
from config import BIRTHDAY_TSTAMP_FORMAT, REMINDER_TSTAMP_FORMAT

from database.controllers.employee_controller import EmployeeController
from database.controllers.subscriber_controller import SubscriberController
from services.translation_service import TranslationService as TS

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from utils.current_time import now

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

    @classmethod
    def calculateNotificaionTime(cls, birth_date, reminder_day_offset) -> pendulum.datetime:
        """
        Calculates the time of the next notification.

        birth_date - Birthday of the employee (as a Pendulum date)
        reminder_day_offset - Offset in days from the birthday.
        """
        birthday_this_year = birth_date.replace(year=now().year)
        if now() > birthday_this_year.subtract(days=reminder_day_offset):
            birthday_this_year = birthday_this_year.add(years=1)
        notification_date = birthday_this_year.subtract(days=reminder_day_offset)

        return notification_date


    @classmethod
    def currentTimeFitsPeriod(cls, date, day_offset) -> bool:
        """
        Checks if the current time is in the given period.

        date - The target date
        day_offset - Offset in days from the date.
        """
        stripped_date = date.replace(year=now().year)
        return stripped_date.subtract(days=day_offset) < now() and now() < stripped_date


    @classmethod
    def isNotificationDue(cls, target_date, reminder_day_offset) -> int:
        """
        Checks if the notification is due.
        Returns -1 if late, 1 if on time, 0 if early

        target_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        notification_due_date = target_date.add(days=reminder_day_offset)

        if now() > notification_due_date:
            return -1  # Late
        elif now() > target_date:
            return 1  # On time
        else:
            return 0  # Early


    @staticmethod
    def datetimeToTimestamp(date_time, format) -> str:
        """
        Converts a DateTime object to a timestamp string in the given format.

        date_time - DateTime object
        format - timestamp format
        """
        return date_time.strftime(format)


    @classmethod
    async def handleEmployeeSchedule(cls, employee) -> bool:
        """
        Sends a notification to the employee if time is due
        and schedules the next notification.
        Returns true if the notification was sent.

        employee - must be an Employee object
        """
        # Parse the birthday string into a Pendulum date object
        birthday_date = pendulum.from_format(employee.birthday, 'DD-MM-YYYY')

        # Generated but will not necessarily be used
        new_scheduled_reminder = cls.calculateNotificaionTime(birthday_date, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Employee has no reminder scheduled, let's fix it
        if employee.scheduled_reminder is None:

            # Sometimes an employee's birthday is inside the notification
            # period when the reminder is not yet scheduled, resulting
            # in a reminder being scheduled for the next year. That's why
            # we need to intervene and send the notification right away.
            if cls.currentTimeFitsPeriod(birthday_date, BIRTHDAY_NOTIFICATION_DAY_OFFSET):
                await cls.broadcastBirthdayNotification(employee)

            employee.scheduled_reminder = cls.datetimeToTimestamp(new_scheduled_reminder, REMINDER_TSTAMP_FORMAT)
            employee.save()
            logger.info(f"{employee.full_name} ({employee.tg_id}) - scheduled for {employee.scheduled_reminder}")

            return False

        due_state = cls.isNotificationDue(new_scheduled_reminder, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Too early, nothing to do
        if due_state == 0:
            logger.info(f"{employee.full_name} ({employee.tg_id}) - nothing to do")
            return False

        # Time to send the notification
        if due_state == 1:
            await cls.broadcastBirthdayNotification(employee)

        # We either got it in time or too late,
        # let's schedule the next notification
        employee.scheduled_reminder = cls.datetimeToTimestamp(new_scheduled_reminder, REMINDER_TSTAMP_FORMAT)
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
