import logging

from database.controllers.user_controller import UserController
from database.application_context import User

logger = logging.getLogger(__name__)


class UserService:
    """
    UserService for user-related actions.
    """
    async def isUserRegistered(tg_user) -> bool:
        """
        Checks if the user with the given Telegram user
        has already been registered.

        tg_user - Telegram user object.
        """
        user = await UserController.getUserByTgId(tg_user.id)
        return True if user else False

    async def userRegister(tg_user) -> User:
        """
        Registers the user with the given Telegram user.

        tg_user - Telegram user object.
        """
        if await UserService.isUserRegistered(tg_user):
            logger.info(f"User {tg_user.id} already registered, skipping")
            return None

        try:
            user = await UserController.addUser(User(
                tg_id=tg_user.id,
                admin=False
            ))

            if user:
                logger.info(f"User {user.tg_id} registered")
            else:
                logger.warning(f"User {tg_user.id} was none after registration")

            return user
        except Exception as e:
            logger.exception(f"Failed to register user: {e}")
