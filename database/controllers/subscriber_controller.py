from database.application_context import AppContext
from database.application_context import Subscriber, User


class SubscriberController():
    async def addSubscriberFromUser(user) -> Subscriber:

        async with AppContext() as database:
            with database.atomic():

                new_subscriber = Subscriber.create(
                    user=user
                )

                new_subscriber.save()
                return new_subscriber


    async def getSubscriberById(id) -> Subscriber:
        async with AppContext() as database:
            with database.atomic():

                return Subscriber.get_or_none(Subscriber.id == id)


    async def getSubscriberByUserId(user_id) -> Subscriber:
        
        async with AppContext() as database:
            with database.atomic():

                return Subscriber.get_or_none(Subscriber.user == user_id)

    
    async def getSubscriberByUserTgId(user_tg_id) -> Subscriber:
        async with AppContext() as database:
            with database.atomic():

                return (Subscriber
                        .select()
                        .join(User)
                        .where(User.tg_id == user_tg_id)
                        .get_or_none())

    
    async def deleteSubscriberById(id) -> bool:
        async with AppContext() as database:
            with database.atomic():

                subscriber = Subscriber.get(Subscriber.id == id)
                subscriber.delete_instance()
                return True

    
    async def deleteSubscriberByUserId(user_id) -> bool:
        async with AppContext() as database:
            with database.atomic():

                subscriber = Subscriber.get(Subscriber.user == user_id)
                subscriber.delete_instance()
                return True

    
    async def deleteSubscriberByUserTgId(user_tg_id) -> bool:
        async with AppContext() as database:
            with database.atomic():

                subscriber = (Subscriber
                              .select()
                              .join(User)
                              .where(User.tg_id == user_tg_id)
                              .get_or_none())

                subscriber.delete_instance()
                return True