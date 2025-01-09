import logging
import time
import datetime
import asyncio
import pendulum

from config import TOKEN
from config import TIMEZONE
from config import BIRTHDAY_NOTIFICATION_DAY_OFFSET
from config import BIRTHDAY_TSTAMP_FORMAT, REMINDER_TSTAMP_FORMAT

from database.controllers.employee_controller import EmployeeController
from database.controllers.subscriber_controller import SubscriberController
from database.controllers.reminder_controller import ReminderController
from database.controllers.user_controller import UserController
from database.application_context import Reminder
from services.translation_service import TranslationService as TS

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.current_time import now

logger = logging.getLogger(__name__)

locale_ru = TS.getTranslation("ru")


class DistributionService:

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
        # period = stripped_date - stripped_date.subtract(days=day_offset) 
        
        return stripped_date.subtract(days=day_offset) < now() and now() < stripped_date.add(days=1)


    @classmethod
    def isNotificationDue(cls, target_date, reminder_day_offset) -> int or bool:
        """
        Checks if the notification is due.
        Returns -1 if late, 1 if on time, 0 if early

        target_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        notification_due_date = target_date.add(days=reminder_day_offset)

        # The notification checked for reminders and that`s why we checked current day
        if reminder_day_offset == 0:
            #return 0 < (now() - target_date).hours and (now() - target_date).hours < 12
            return target_date.add(hours=8) < now() and now() < target_date.add(hours=18)

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
        birthday_date = pendulum.from_format(employee.birthday, 'DD-MM-YYYY', tz=TIMEZONE)

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

        employee_birthday = pendulum.from_format(employee.birthday, "DD-MM-YYYY").replace(year=now().year).format("DD-MM-YYYY")

        template = TS.getTemplate(locale_ru, "birthdayNotification")
        message_text = template.format(
            employee=employee.full_name,
            date=employee.birthday
        )

        button_text = TS.getTemplate(locale_ru, "reminderButton")

        button = InlineKeyboardButton(
            text=button_text, 
            callback_data=f"reminder:{employee.id}:{employee_birthday}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]], resize_keyboard=True)

        # List of task to be run in parallel
        tasks = [
            cls.bot.send_message(
                chat_id=subscriber.tg_id,
                text=message_text,
                reply_markup=keyboard
                )
            for subscriber in subscribers
        ]
        

        # Running the tasks
        await asyncio.gather(*tasks)
        logger.info(f"{employee.full_name} ({employee.tg_id}) - finished broadcasting.")

        return True


    @classmethod
    async def createReminder(cls, user_tg_id, employee_id, date) -> bool:
        """
        Creates a reminder for the employee.

        user_tg_id - id of the Telegram user
        employee_id - id of the employee
        date - for which date to create the reminder
        """
        user = await UserController.getUserByTgId(user_tg_id)
        employee = await EmployeeController.getEmployeeById(employee_id)

        # Check if the date is in the expired
        date = pendulum.from_format(date, "DD-MM-YYYY")
        if date <= now():
            logger.info(f"{employee.full_name} ({employee.tg_id}) - date is expired")
            return False

        # Check if the user already has a reminder
        try:
            remind = await ReminderController.getReminderByEmployeeIdAndUserId(user.id, employee.id)
            logger.info(f"{employee.full_name} ({employee.tg_id}) - user already has a reminder")
            return False
        except Exception:
            pass
        
        await ReminderController.addReminderFromUserAndEmployee(user, employee, date.format("DD-MM-YYYY"))

        return True


    @classmethod
    async def handleReminderSchedule(cls, reminder) -> bool:
        """
        Handles the reminder for the employee.

        reminder - must be a Reminder object
        """
        reminder_date = pendulum.from_format(reminder.date, "DD-MM-YYYY", tz=TIMEZONE)


        due_state = cls.isNotificationDue(reminder_date, 0)

        # Time to send the notification
        if due_state == 1:
            user = await UserController.getUserById(reminder.user_id)
            template = TS.getTemplate(locale_ru, "reminderNotification")
            employee = await EmployeeController.getEmployeeById(reminder.employee_id)
            message_text = template.format(
                employee=employee.full_name,
            )
            await cls.bot.send_message(
                chat_id=user.tg_id,
                text=message_text
            )
            
            await ReminderController.deleteReminderById(reminder.id)
        
        # Too early, nothing to do
        if due_state == 0:
            logger.info(f"({reminder.id}) - too early")


        logger.info(f"({reminder.id}) - nothing to do")

        return False


    @classmethod
    async def birthdayCycle(cls, forever=False, interval=600) -> None:
        """
        Handles birthday notifications at fixed periods of time.
        """
        # Avoid overloading
        if interval is None or interval < 60:  # 1 minute
            raise ValueError("Cycle interval must be at least 1 minute.")

        while True:
            for employee in await EmployeeController.getEmployees():
                try:
                    await cls.handleEmployeeSchedule(employee)
                except Exception as e:
                    logger.exception(f"Failed to send birthday notification: {e}")

            for reminder in await ReminderController.getReminders():
                try:
                    await cls.handleReminderSchedule(reminder)
                except Exception as e:
                    logger.exception(f"Failed to send reminder notification: {e}")
                    
            if not forever:
                break

            await asyncio.sleep(interval)
            
