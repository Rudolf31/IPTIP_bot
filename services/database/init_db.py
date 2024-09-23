import aiosqlite
from config import DATABASE

async def init_db():

    global DATABASE

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id BIGINT NOT NULL,
                admin BOOLEAN
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birthday TIMESTAMP NOT NULL,
                tg_id BIGINT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (employee_id) REFERENCES Employees(id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        ''')
        await db.commit()
