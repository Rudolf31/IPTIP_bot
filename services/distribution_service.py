import logging
import time
from datetime import date

from config import BIRTHDAY_NOTIFICATION_DAY_OFFSET

from database.controllers.employee_controller import EmployeeController

logger = logging.getLogger(__name__)

class DistributionService:

    year_seconds = 31556952
    day_seconds = 86400
    
    @classmethod
    def calculateNotificaionTime(cls, birth_date, reminder_day_offset):
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
    def isNotificationDue(cls, target_date, reminder_day_offset):
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
    async def employeeBirthdayNotification(cls, employee):
        """
        Sends a notification to the employee

        employee - must be an Employee object
        """
        if employee.scheduled_reminder is None:
            employee.scheduled_reminder = cls.calculateNotificaionTime(employee.birthday, BIRTHDAY_NOTIFICATION_DAY_OFFSET)
            logger.info(f"{employee.full_name} ({employee.tg_id}) - reminder set to {employee.scheduled_reminder}")
            return

        due_state = cls.isNotificationDue(employee.scheduled_reminder, BIRTHDAY_NOTIFICATION_DAY_OFFSET)

        if due_state == 1:

            # Send notification in Telegram here
            # If sent successfully, update the reminder time
            
            employee.scheduled_reminder = cls.calculateNotificaionTime(employee.birthday, BIRTHDAY_NOTIFICATION_DAY_OFFSET)
            employee.save()

        if due_state == -1:
            employee.scheduled_reminder = cls.calculateNotificaionTime(employee.birthday, BIRTHDAY_NOTIFICATION_DAY_OFFSET)
            employee.save()

