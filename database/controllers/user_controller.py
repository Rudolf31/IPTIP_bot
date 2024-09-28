from database.application_context import AppContext
from database.application_context import User


class UserController():
    async def addUser(user) -> User:

        async with AppContext() as database:
            new_user = User.create(tg_id=user.tg_id, admin=user.admin)
            new_user.save()
            return new_user


    async def getUserById(id) -> User:

        async with AppContext() as database:
            return User.get(User.id == id)


    async def getUserByTgId(tg_id) -> User:

        async with AppContext() as database:
            return User.get(User.tg_id == tg_id)

    
    async def delUser(id) -> bool:

        async with AppContext() as database:
            user = User.get(User.id == id)
            user.delete_instance()
            return True

    
    async def updateUser(user) -> bool:

        async with AppContext() as database:
            user.save()
            return True