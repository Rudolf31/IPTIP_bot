from warnings import deprecated

from database.application_context import AppContext
from database.application_context import Subscriber, User


class SubscriberController():
    """
    SubscriberController for database actions
    related to subscribers.
    """
    @deprecated("Redundant object copying. Switch to addSubscriberFromUserId.")
    async def addSubscriberFromUser(user) -> Subscriber:
        """
        Addition of a new subscriber.

        user - must be a User object.
        """

        async with AppContext() as database:
            with database.atomic():

                new_subscriber = Subscriber.create(
                    user=user
                )

                new_subscriber.save()
                return new_subscriber

    async def addSubscriberFromUserId(user_id) -> Subscriber:
        """
        Addition of a new subscriber.

        user_id - id of the user.
        """
        async with AppContext() as database:
            with database.atomic():

                new_subscriber = Subscriber.create(
                    user=user_id
                )

                new_subscriber.save()
                return new_subscriber

    async def getSubscriberById(id) -> Subscriber:
        """
        Returns the Subscriber object from the database that
        matches the given id.

        id - id of Subscriber.
        """
        async with AppContext() as database:
            with database.atomic():

                return Subscriber.get_or_none(Subscriber.id == id)

    async def getSubscriberByUserId(user_id) -> Subscriber:
        """
        Returns the Subscriber object from the database that
        matches the given user id.

        user_id - id of the user.
        """
        async with AppContext() as database:
            with database.atomic():

                return Subscriber.get_or_none(Subscriber.user == user_id)

    async def getSubscriberByUserTgId(user_tg_id) -> Subscriber:
        """
        Returns the Subscriber object from the database that
        matches the given Telegram user id.

        id - id of the Telegram user.
        """
        async with AppContext() as database:
            with database.atomic():

                return (Subscriber
                        .select()
                        .join(User)
                        .where(User.tg_id == user_tg_id)
                        .get_or_none())

    async def getSubscribers() -> list:
        """
        Returns all subscribers from the database.
        """
        async with AppContext() as database:
            with database.atomic():

                return list(Subscriber.select())

    async def deleteSubscriberById(id) -> bool:
        """
        Deletes the subscriber that matches the subscriber id from
        the database. Returns true on success.

        id - id of Subscriber.
        """
        async with AppContext() as database:
            with database.atomic():

                subscriber = Subscriber.get(Subscriber.id == id)
                subscriber.delete_instance()
                return True

    async def deleteSubscriberByUserId(user_id) -> bool:
        """
        Deletes the subscriber that matches the user id from
        the database. Returns true on success.

        id - id of User.
        """
        async with AppContext() as database:
            with database.atomic():

                subscriber = Subscriber.get(Subscriber.user == user_id)
                subscriber.delete_instance()
                return True

    async def deleteSubscriberByUserTgId(user_tg_id) -> bool:
        """
        Deletes the subscriber that matches the Telegram user id from
        the database. Returns true on success.

        id - id of Telegram user.
        """
        async with AppContext() as database:
            with database.atomic():

                subscriber = (Subscriber
                              .select()
                              .join(User)
                              .where(User.tg_id == user_tg_id)
                              .get_or_none())

                subscriber.delete_instance()
                return True
