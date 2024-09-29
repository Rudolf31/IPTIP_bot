from database.application_context import AppContext
from database.application_context import Reminder, User, Employee

class ReminderController():
    async def addReminderFromUserAndEmployee(user, employee) -> Reminder:

        async with AppContext() as database:
            with database.atomic():

                new_reminder = Reminder.create(
                    user=user,
                    employee=employee
                )

                new_reminder.save()

                return new_reminder

    async def getReminderById(id) -> Reminder:
            async with AppContext() as database:
                with database.atomic():

                    return Reminder.get(Reminder.id == id)

    async def getRemindersByUserId(user_id) -> Reminder:
        async with AppContext() as database:
            with database.atomic():

                return Reminder.select().where(Reminder.user == user_id)


    async def deleteReminderById(id) -> bool:
        async with AppContext() as database:
            with database.atomic():

                reminder = Reminder.get(Reminder.id == id)
                reminder.delete_instance()
                return True


    async def deleteRemindersByUserId(user_id) -> bool:
        async with AppContext() as database:
            with database.atomic():

                reminders = Reminder.select().where(Reminder.user == user_id)
                for reminder in reminders:
                    reminder.delete_instance()
                return True
