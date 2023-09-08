import asyncio
import aiosqlite


async def create_conn():
    db = Sqlite3Class()
    await db._init()

    return db


class Sqlite3Class:
    # async def __init__(self, loop):
    # pass
    # self.conn = await aiosqlite.connect("pythonsqlite.db", loop=loop)
    # self.cursor = await self.conn.cursor()
    # self.cursor.row_factory = lambda cursor, row: row[0]

    async def _init(self):
        self.conn = await aiosqlite.connect("db_idhistory.db")
        # self.conn.row_factory = lambda cursor, row: row[0]
        # self.conn.row_factory = aiosqlite.Row
        self.cursor = await self.conn.cursor()
        print("init aiosqliteclass done ")

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
        await self.cursor.execute(
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
        print("inserted id request")

    async def query_history_all(self):
        #  returns all history
        await self.cursor.execute("SELECT * FROM chuntfm")
        result = await self.cursor.fetchall()
        if result:
            return result

        else:
            return None

    async def query_history_user(self, username):
        #  returns all history
        await self.cursor.execute("SELECT * FROM chuntfm WHERE username=? ", [username])
        result = await self.cursor.fetchall()
        if result:
            return result

        else:
            return None


async def run(loop, query_in):
    db = await create_conn()
    await db.insert_id_request(*query_in)
    r = await db.query_history_all()
    if r:
        for result in r:
            print(result)
    """
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM tag_table WHERE tag_name=? ", ['woi',])
        r = await cur.fetchall()
        print(r)
    """
    await db.conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # query_in = input("enter search term: ")
    # url_in = input("enter url: ")
    query_in = [
        "2023-09-06T15:02:26Z",
        "knmx",
        "chuntoo",
        "id1",
        "chuntfm",
        "anon livestream",
        "unknown artists",
        "good music",
        "http://bla",
        "shazam says bla",
        None,
    ]
    # task = asyncio.gather(run())
    try:
        loop.run_until_complete(run(loop, query_in))
        # loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        # task.cancel()
        loop.close()
