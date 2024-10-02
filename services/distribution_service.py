import logging
import time

from config import BIRTHDAY_NOTIFICATION_DAY_OFFSET
from config import BIRTHDAY_TSTAMP_FORMAT, REMINDER_TSTAMP_FORMAT

from database.controllers.employee_controller import EmployeeController

logger = logging.getLogger(__name__)


class DistributionService:

    year_seconds = 31556952
    day_seconds = 86400

    # TODO: find out what this function actually returns
    # (God I hate Python)
    @classmethod
    def calculateNotificaionTime(cls, birth_date, reminder_day_offset) -> int:
        """
        Calculates the time of the next notification.

        birth_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        current_year = time.localtime().tm_year  # 2024
        stripped_reminder_date = (birth_date - reminder_day_offset * cls.day_seconds) % cls.year_seconds  # 01.08.____
        stripped_date_now = time.time() % cls.year_seconds  # 01.02.____

        # If current stripped day is > stripped reminder date, then add 1 year
        extra_years = 1 if stripped_reminder_date < stripped_date_now else 0

        return (current_year + extra_years) * cls.year_seconds + stripped_reminder_date

    @classmethod
    def isNotificationDue(cls, target_date, reminder_day_offset) -> int:
        """
        Checks if the notification is due.
        Returns true if the notification is due.
        Returns false if early or late

        target_date - Birthday of the employee
        reminder_day_offset - Offset in days from the birthday.
        """
        # FIXME: I feel like we could do a cleaner implementation
        # since it is not very clear what the integers mean in the
        # return values. Something like enums would probably
        # do better (WeirdCat 02.10.2024)
        current_time = time.time()
        if current_time > target_date + (reminder_day_offset * cls.day_seconds):
            return -1  # Late
        elif current_time > target_date:
            return 1  # On time
        else:
            return 0  # Early

    # FIXME: This function should utilize datetimes for it in order to be
    # possible to save reminders in the database (it uses timestamps afterall).
    # For now does not function at all
    @classmethod
    async def employeeBirthdayNotification(cls, employee) -> bool:
        """
        Sends a notification to the employee if time is due
        and schedules the next notification.
        Returns true if the notification was sent.

        Assumes that the employee birthday is in the format
        dd-mm-yyyy.
        Uses dd-mm-yyyy hh:mm:ss for reminder time.

        employee - must be an Employee object
        """
        # Since the birthday is in the format dd-mm-yyyy
        birthday_timestamp = time.strptime(employee.birthday, BIRTHDAY_TSTAMP_FORMAT)

        # Generated but will not necessarily be used
        new_scheduled_reminder = cls.calculateNotificaionTime(birthday_timestamp, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Employee has no reminder scheduled, let's fix it
        if employee.scheduled_reminder is None:
            employee.scheduled_reminder = time.strftime(REMINDER_TSTAMP_FORMAT, new_scheduled_reminder)
            logger.info(f"{employee.full_name} ({employee.tg_id}) - reminder set to {employee.scheduled_reminder}")
            return False

        # Checking scheduled notification time to see if we should do anything
        scheduled_reminder_unix = time.strptime(employee.scheduled_reminder, REMINDER_TSTAMP_FORMAT)
        due_state = cls.isNotificationDue(scheduled_reminder_unix, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Too early, nothing to do
        if due_state == 0:
            return False

        # Time to send the notification
        if due_state == 1:

            # Send notification in Telegram here
            # If not sent successfully, throw error
            logger.info(f"{employee.full_name} ({employee.tg_id}) - birthday notifications supposed to be sent")

        # We either got it in time or too late,
        # let's schedule the next notification
        employee.scheduled_reminder = time.strftime(REMINDER_TSTAMP_FORMAT, new_scheduled_reminder)
        employee.save()

        logger.info(f"{employee.full_name} ({employee.tg_id}) - reminder set to {employee.scheduled_reminder}")

        return False

    @classmethod
    async def employeeBirthdayNotificationById(cls, id) -> bool:
        """
        Wrapper of employeeBirthdayNotification to be
        used with the id of the employee.

        id - id of Employee.
        """
        employee = await EmployeeController.getEmployeeById(id)
        return await cls.employeeBirthdayNotification(employee)
