from peewee import SqliteDatabase
from config import DATABASE
from database.models import User, Employee, Reminder, Subscriber



class AppContext:
    def __init__(self):
        self.database = SqliteDatabase(DATABASE)

    async def __aenter__(self):
        
        self.database.connect()
        
        await self.database.create_tables([User, Employee, Reminder, Subscriber], safe=True)
        return self.database

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        
        self.database.close()