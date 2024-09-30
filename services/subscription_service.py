import logging

from database.controllers.subscriber_controller import SubscriberController
from database.controllers.user_controller import UserController

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    SubscriptionService is responsible for
    subscription-related actions.
    """

    async def setUserSubscriptionState(user_tg_id, state) -> bool:
        """
        Sets the subscription state of the user.

        user_tg_id - id of the Telegram user.
        state - new subscription state.
        """
        user = await UserController.getUserByTgId(user_tg_id)

        if not user:
            logger.exception(f"Failed to set subscription state for Telegram user {user_tg_id} since it was not found in the database")
            return False
        
        old_state = await SubscriberController.getSubscriberByUserId(user.id) != None
        if old_state == state:
            return True
        
        if state:
            user = await SubscriberController.addSubscriberFromUser(user)
        else:
            user = await SubscriberController.deleteSubscriberByUserId(user.id)

        logger.info(f"User {user_tg_id} {'' if state else 'un'}subscribed")
        
        return True