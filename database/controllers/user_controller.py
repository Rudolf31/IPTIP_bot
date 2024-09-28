from database.application_context import AppContext
from database.application_context import User


class UserController():
    async def addUser(user) -> User:

        async with AppContext() as database:
            new_user = User.create(tg_id=user.tg_id, admin=user.admin)
            new_user.save()
            return new_user
