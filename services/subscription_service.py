import logging

from database.controllers.subscriber_controller import SubscriberController
from database.controllers.user_controller import UserController

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    SubscriptionService is responsible for
    subscription-related actions.
    """

    async def getUserSubscriptionState(user_tg_id) -> bool:
        """
        Returns the subscription state of the user.
        Returns true if the user is subscribed,
        otherwise false.

        user_tg_id - id of the Telegram user.
        """
        user = await UserController.getUserByTgId(user_tg_id)

        if not user:
            logger.warn(f"Failed to get subscription state for "
                        f"Telegram user {user_tg_id} since it "
                        f"was not found in the database.")
            return False

        return await SubscriberController.getSubscriberByUserId(user.id) is not None

    @classmethod
    async def setUserSubscriptionState(cls, user_tg_id, state) -> bool:
        """
        Sets the subscription state of the user.
        Returns true on success.

        user_tg_id - id of the Telegram user.
        state - new subscription state.
        """
        user = await UserController.getUserByTgId(user_tg_id)

        if not user:
            logger.exception(f"Failed to set subscription state for "
                             f"Telegram user {user_tg_id} since it "
                             f"was not found in the database.")
            return False

        old_state = await cls.getUserSubscriptionState(user_tg_id)
        if old_state == state:
            return True  # Nothing to do

        if state:
            user = await SubscriberController.addSubscriberFromUserId(user.id)
        else:
            user = await SubscriberController.deleteSubscriberByUserId(user.id)

        logger.info(f"User {user_tg_id} {'' if state else 'un'}subscribed.")

        return True
