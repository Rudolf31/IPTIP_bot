from database.application_context import AppContext
from database.application_context import Reminder


class ReminderController():
    """
    Reminder table, representing extra birthday reminders that a subscriber
    can request for the birthday of a particular employee.
    """
    async def addReminderFromUserAndEmployee(user, employee) -> Reminder:
        """
        Addition of a new reminder.

        user - must be a User object.
        employee - must be a Employee object.
        """
        async with AppContext() as database:
            with database.atomic():

                new_reminder = Reminder.create(
                    user=user,
                    employee=employee
                )

                new_reminder.save()

                return new_reminder

    async def getReminderById(id) -> Reminder:
        """
        Returns the Reminder object from the database that
        matches the given id.

        id - id of Reminder.
        """
        async with AppContext() as database:
            with database.atomic():

                return Reminder.get(Reminder.id == id)

    async def getRemindersByUserId(user_id) -> Reminder:
        """
        Returns the Reminder object from the database that
        matches the given user id.

        id - id of the user.
        """
        async with AppContext() as database:
            with database.atomic():

                return Reminder.select().where(Reminder.user == user_id)

    async def deleteReminderById(id) -> bool:
        """
        Deletes the reminder that matches the reminder id from
        the database. Returns true on success.

        id - id of Reminder.
        """
        async with AppContext() as database:
            with database.atomic():

                reminder = Reminder.get(Reminder.id == id)
                reminder.delete_instance()
                return True

    async def deleteRemindersByUserId(user_id) -> bool:
        """
        Deletes the reminders that match the user id from
        the database. Returns true on success.

        id - id of User.
        """
        async with AppContext() as database:
            with database.atomic():

                reminders = Reminder.select().where(Reminder.user == user_id)
                for reminder in reminders:
                    reminder.delete_instance()
                return True
