from database.application_context import AppContext


async def user_controller():
    async with AppContext() as database:
        # Здесь вы можете выполнять операции с базой данных
        pass