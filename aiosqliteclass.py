import asyncio
import aiosqlite
import logging as LOGGER


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
        self.conn = await aiosqlite.connect("pythonsqlite.db")
        self.conn.row_factory = lambda cursor, row: row[0]
        # self.conn.row_factory = aiosqlite.Row
        self.cursor = await self.conn.cursor()
        print("init aiosqliteclass done ")

    async def _close():
        await self.conn.close()

    async def query_gif(self, inurl):
        # inurl: url
        # returns url id
        print("query_gif", inurl)
        await self.cursor.execute(
            "SELECT * FROM object_table WHERE object_name=? ", [inurl]
        )
        result = await self.cursor.fetchone()
        if result:
            result_id = result
            return result_id
        else:
            return None

    async def query_tag(self, intag):
        # intag: gif tag to search
        #  returns tag id
        query_tag = intag
        await self.cursor.execute(
            "SELECT * FROM tag_table WHERE tag_name=? ", [query_tag]
        )
        result = await self.cursor.fetchone()
        if result:
            result_tag = result
            result_tag_id = result_tag
            return result_tag_id

        else:
            return None

    async def create_tag(self, intag):
        # intag: tag name to create
        # returns id of created tag
        query_tag = intag
        await self.cursor.execute(
            "INSERT INTO tag_table (tag_name) VALUES (?)", [intag]
        )
        await self.conn.commit()
        result_tag_id = self.cursor.lastrowid
        return result_tag_id

    async def map_tag_to_gif(self, tagid, gifid):
        # tag id: tag id to map to gif
        # gif id: gif id to map to tag

        try:
            await self.cursor.execute(
                "INSERT INTO object_tag_mapping VALUES (?,?)", (gifid, tagid)
            )
            await self.conn.commit()
        except Exception as e:
            print(e)
            pass

    async def fetch_gif(self, intag):
        # intag: tag name to search
        # returns gif url
        await self.cursor.execute(
            "SELECT object_name from object_tag_mapping JOIN object_table ON object_reference = object_table.id JOIN tag_table ON tag_reference = tag_table.id WHERE tag_name = ?",
            [intag],
        )
        result = await self.cursor.fetchall()
        return result

    async def insert(self, inurl):
        await self.cursor.execute(
            "INSERT INTO object_table (object_name) VALUES (?)", [inurl]
        )
        await self.conn.commit()
        result_tag_id = self.cursor.lastrowid
        return result_tag_id

    async def tag(self, inurl, intag):
        print("tag")
        urlid = await self.query_gif(inurl)
        print("tag urlid", urlid)
        if not urlid:
            urlid = await self.insert(inurl)
        tagid = await self.query_tag(intag)
        print("tag tagid", tagid)
        if not tagid:
            tagid = await self.create_tag(intag)
        await self.map_tag_to_gif(tagid, urlid)

    async def untag(self, inurl, intag):
        urlid = await self.query_gif(inurl)
        tagid = await self.query_tag(intag)
        print(urlid)
        print(tagid)
        if urlid and tagid:
            await self.cursor.execute(
                "DELETE FROM object_tag_mapping  WHERE object_reference = ? AND tag_reference = ?",
                (urlid, tagid),
            )
            await self.conn.commit()

        test_tag_has_url = await self.fetch_gif(intag)
        print(test_tag_has_url)

        if not test_tag_has_url:
            await self.cursor.execute(
                "DELETE FROM tag_table WHERE tag_name = ?", (intag,)
            )
            await self.conn.commit()

    async def info(self, in_string):
        # in_string could be either url or tag name
        # returns corresponding tag names or urls
        resulting_tags = []
        resulting_urls = []
        await self.cursor.execute(
            "SELECT object_name from object_tag_mapping JOIN object_table ON object_reference = object_table.id JOIN tag_table ON tag_reference = tag_table.id WHERE tag_name = ?",
            [in_string],
        )
        result = await self.cursor.fetchall()
        resulting_urls.append(result)

        await self.cursor.execute(
            "SELECT tag_name from object_tag_mapping JOIN tag_table ON tag_reference = tag_table.id JOIN object_table ON object_reference = object_table.id WHERE object_name = ?",
            [in_string],
        )
        result = await self.cursor.fetchall()
        resulting_tags.append(result)
        print(resulting_tags, resulting_urls)
        return resulting_urls, resulting_tags


async def run(loop, query_in):
    db = await create_conn()
    r = await db.info(query_in)
    print(r)
    """
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM tag_table WHERE tag_name=? ", ['woi',])
        r = await cur.fetchall()
        print(r)
    """
    await db.conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    query_in = input("enter search term: ")
    # url_in = input("enter url: ")

    # task = asyncio.gather(run())
    try:
        loop.run_until_complete(run(loop, query_in))
        # loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        # task.cancel()
        loop.close()
