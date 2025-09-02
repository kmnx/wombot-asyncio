import asyncio
import aiosqlite
from helpers.db_sqlite import AsyncDB


class DB_ShazamIDs(AsyncDB):
    async def _init(self):
        self.conn = await aiosqlite.connect(self.db_name)
        # self.conn.row_factory = lambda cursor, row: row[0]
        # self.conn.row_factory = aiosqlite.Row

        await self.conn.execute(
            "CREATE TABLE IF NOT EXISTS chuntfm (id INTEGER PRIMARY KEY, timestamp_utc, username, request_source, request_command, station, show_name, artist, title, bandcamp, shazam_result, verified);"
        )

    async def _close(self):
        await self.conn.close()

    async def insert_id_request(
        self,
        timestamp_utc,
        username,
        request_source,
        request_command,
        station,
        show_name,
        artist,
        title,
        bandcamp,
        shazam_result,
        verified,
    ):
        await self.conn.execute(
            "INSERT INTO chuntfm (timestamp_utc, username, request_source, request_command, station, show_name, artist, title, bandcamp, shazam_result, verified) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                str(timestamp_utc),
                username,
                request_source,
                request_command,
                station,
                show_name,
                artist,
                title,
                bandcamp,
                str(shazam_result),
                verified,
            ],
        )
        await self.conn.commit()
        # result_tag_id = self.cursor.lastrowid
        # return result_tag_id

    async def query_history_all(self):
        #  returns all history
        async with self.conn.execute("SELECT * FROM chuntfm") as cursor:
            result = await cursor.fetchall()
            if result:
                return result
            else:
                return None

    async def query_usernames(self):
        #  returns all history
        async with self.conn.execute(
            "SELECT username FROM chuntfm ORDER BY username DESC"
        ) as cursor:
            result = await cursor.fetchall()
            if result:
                return result

            else:
                return None

    async def query_history_user(self, username):
        #  returns all history
        async with self.conn.execute(
            "SELECT * FROM chuntfm WHERE username=? ", [username]
        ) as cursor:
            result = await cursor.fetchall()
            if result:
                return result

            else:
                return None


