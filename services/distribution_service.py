import logging
import time


from database.controllers.employee_controller import EmployeeController

logger = logging.getLogger(__name__)

class DistributionService:

    def calculateNotificaionTime(birth_date, reminder_day_offset):
        """
        Calculates the time of the next notification.

        birth_date - Birthday of the employee.
        reminder_day_offset - Offset in days from the birthday.
        """
        year_seconds = 31556952
        day_seconds = 86400

        current_year = time.localtime().tm_year  # 2024
        stripped_reminder_date = (birth_date - reminder_day_offset * day_seconds) % year_seconds  # 01.08.____
        stripped_date_now = time.time() % year_seconds  # 01.02.____

        # If current stripped day is > stripped reminder date, then add 1 year
        extra_years = 1 if stripped_reminder_date < stripped_date_now else 0

        return (current_year + extra_years) * year_seconds + stripped_reminder_date








    # async def scheduleBirthdayNotification(employee):
    #     if employee.scheduled_reminder is None:
    #         birthdate = employee.birthday % 31556952
    #         datenow = time.time() % 31556952

    #         if birthdate < datenow:
    #             current_year = time.localtime().tm_year
    #             employee.scheduled_reminder = birthdate + (current_year + 1) * 31556952

    #         else:
    #             employee.scheduled_reminder = birthdate + current_year * 31556952

    #         employee.scheduled_reminder -= 3 * 86400

    #         await EmployeeController.updateEmployee(employee)
    #     if  employee.scheduled_reminder <= time.time() + 3 * 86400 and employee.scheduled_reminder > time.time():
    #         # Send birthday notification, update scheduled_reminder
    #         pass
    #     if  