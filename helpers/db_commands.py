from datetime import datetime, timedelta
import logging

import aiosqlite
from helpers.db_sqlite import AsyncDB

logger = logging.getLogger(__name__)


class DB_Commands(AsyncDB):
    async def _init(self):
        self.conn = await aiosqlite.connect(self.db_name)
        # self.conn.row_factory = lambda cursor, row: row[0]
        # self.conn.row_factory = aiosqlite.Row

        await self.create_commands_table(self.conn)

    async def _close(self):
        await self.conn.close()

    async def create_commands_table(self):
        await self.conn.execute(
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
        await self.conn.commit()

    async def insert_command(self, command, username, channel):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        await self.conn.execute(
            """
            INSERT INTO commands (command, time, date, username, channel)
            VALUES (?, ?, ?, ?, ?)
        """,
            (command, current_time, current_date, username, channel),
        )
        await self.conn.commit()

    async def get_most_used_commands(self):
        # Calculate the date 7 days ago from today
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        async with self.conn.execute(
            """
            SELECT command, COUNT(*) as command_count
            FROM commands
            WHERE date >= ?
            GROUP BY command
            ORDER BY command_count DESC
            LIMIT 10
        """,
            (seven_days_ago,),
        ) as cursor:

            rows = await cursor.fetchall()

            return rows
