from datetime import datetime, timedelta

import aiosqlite

from wombot import logger


async def create_commands_table(connection):
    cursor = await connection.cursor()
    await cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            time TEXT,
            date TEXT,
            username TEXT,
            channel TEXT
        )
    """
    )
    await connection.commit()


async def insert_command(connection, command, username, channel):
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")

    cursor = await connection.cursor()
    await cursor.execute(
        """
        INSERT INTO commands (command, time, date, username, channel)
        VALUES (?, ?, ?, ?, ?)
    """,
        (command, current_time, current_date, username, channel),
    )
    await connection.commit()


async def get_most_used_commands(connection):
    # Calculate the date 7 days ago from today
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor = await connection.cursor()
    await cursor.execute(
        """
        SELECT command, COUNT(*) as command_count
        FROM commands
        WHERE date >= ?
        GROUP BY command
        ORDER BY command_count DESC
        LIMIT 10
    """,
        (seven_days_ago,),
    )

    rows = await cursor.fetchall()

    return rows


async def get_db_idhistory_cur():
    # ugh
    logger.debug("get_db_cur")

    conn = await aiosqlite.connect("/db/trackids.db")
    # conn.row_factory = lambda cursor, row: row[0]
    # self.conn.row_factory = aiosqlite.Row
    cursor = await conn.cursor()
    return cursor
