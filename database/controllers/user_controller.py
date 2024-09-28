from database.application_context import AppContext
from database.application_context import User


class UserController():
    """
    UserController for database actions related to User.
    """
    async def addUser(user) -> User:
        """
        Addition of a new user.

        user - must be a new User object.
        """
        async with AppContext() as database:
            with database.atomic():

                new_user = User.create(tg_id=user.tg_id, admin=user.admin)
                new_user.save()
                return new_user

    async def getUserById(id) -> User:
        """
        Returns the User object from the database that
        matches the given id.

        id - id of User (do not confuse with Telegram ID)
        """

        async with AppContext() as database:
            with database.atomic():

                return User.get(User.id == id)

    async def getUserByTgId(tg_id) -> User:
        """
        Returns the User object from the database that
        matches the given Telegram user id.

        id - id of the Telegram user.
        """

        async with AppContext() as database:
            with database.atomic():

                return User.get(User.tg_id == tg_id)

    async def deleteUser(id) -> bool:
        """
        Deletes the user that matches the user id from
        the database. Returns true on success.

        id - id of User (do not confuse with Telegram ID)
        """

        async with AppContext() as database:
            with database.atomic():

                user = User.get(User.id == id)
                user.delete_instance()
                return True

    async def updateUser(user) -> bool:
        """
        Updates the given user's parameters. Returns true
        if successful.

        user - User object
        """

        async with AppContext() as database:
            with database.atomic():

                user.save()
                return True
