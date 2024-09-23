from peewee import SqliteDatabase
from config import DATABASE
from services.database.models import User, Employee, Reminder, Subscriber

db = SqliteDatabase(DATABASE)

async def init_db():
    await db.create_tables([User, Employee, Reminder, Subscriber])