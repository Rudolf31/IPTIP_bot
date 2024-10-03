import logging
import time
import datetime

from config import ENVIRONMENT
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
        current_year = time.localtime().tm_year - 1970  # 2024
        stripped_reminder_date = (birth_date - reminder_day_offset * cls.day_seconds) % cls.year_seconds  # 01.08.____
        stripped_date_now = time.time() % cls.year_seconds  # 01.02.____

        # If current stripped day is > stripped reminder date, then add 1 year
        extra_years = 1 if stripped_reminder_date < stripped_date_now else 0

        return (current_year + extra_years) * cls.year_seconds + stripped_reminder_date

    @classmethod
    def isNotificationDue(cls, target_date, reminder_day_offset) -> int:
        """
        Checks if the notification is due.
        Returns -1 if late, 1 if on time, 0 if early

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

    # TODO: heavy testing (pls halp)
    @classmethod
    async def employeeBirthdayNotification(cls, employee) -> bool:
        """
        Sends a notification to the employee if time is due
        and schedules the next notification.
        Returns true if the notification was sent.

        employee - must be an Employee object
        """
        # Since the birthday is in a timestamp format
        # birthday_timestamp = int(time.mktime(time.strptime(employee.birthday, BIRTHDAY_TSTAMP_FORMAT)))
        birthday_timestamp = int(datetime.datetime.strptime(employee.birthday, BIRTHDAY_TSTAMP_FORMAT).timestamp())

        # Generated but will not necessarily be used
        new_scheduled_reminder = cls.calculateNotificaionTime(birthday_timestamp, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Employee has no reminder scheduled, let's fix it
        # TODO the algorithm should be further thought over and preferably optimized
        if employee.scheduled_reminder is None:
            reminder_without_offset = cls.calculateNotificaionTime(birthday_timestamp, 0)

            if time.time() < reminder_without_offset and time.time() > (new_scheduled_reminder - cls.year_seconds):
                logger.info(f"{employee.full_name} ({employee.tg_id}) - birthday notifications supposed to be sent")
                # TODO we need to send the notification here

            employee.scheduled_reminder = datetime.datetime.fromtimestamp(new_scheduled_reminder).strftime(REMINDER_TSTAMP_FORMAT)
            logger.info(f"{employee.full_name} ({employee.tg_id}) - reminder set to {employee.scheduled_reminder}")
            employee.save()
            #FIXME: here we should also check if the notification was sent, thats why return here is a mistake
            return False

        # Checking scheduled notification time to see if we should do anything
        # scheduled_reminder_unix = int(time.mktime(time.strptime(employee.scheduled_reminder, REMINDER_TSTAMP_FORMAT)))
        scheduled_reminder_unix = int(datetime.datetime.strptime(employee.scheduled_reminder, REMINDER_TSTAMP_FORMAT).timestamp())
        due_state = cls.isNotificationDue(scheduled_reminder_unix, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        # Too early, nothing to do
        if due_state == 0:
            logger.info(f"{employee.full_name} ({employee.tg_id}) - nothing to do")
            return False

        # Time to send the notification
        if due_state == 1:

            # Send notification in Telegram here
            # If not sent successfully, throw error
            logger.info(f"{employee.full_name} ({employee.tg_id}) - birthday notifications supposed to be sent")

        # We either got it in time or too late,
        # let's schedule the next notification
        employee.scheduled_reminder = datetime.datetime.fromtimestamp(new_scheduled_reminder).strftime(REMINDER_TSTAMP_FORMAT)
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
