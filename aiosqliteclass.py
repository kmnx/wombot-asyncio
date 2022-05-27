import asyncio
import aiosqlite
import logging as LOGGER


class sqlite3class:
    async def __init__(self):
        self.conn = await aiosqlite.connect("pythonsqlite.db")
        self.cursor = await self.conn.cursor()
        self.cursor.row_factory = lambda cursor, row: row[0]

    async def query_gif(self, inurl):
        # inurl: url
        # returns url ID
        await print("query_gif", inurl)
        await self.cursor.execute("SELECT * FROM object_table WHERE object_name=? ", [inurl])
        result = await self.cursor.fetchone()
        if result:
            result_id = result
            return result_id
        else:
            return None

    async def query_tag(self, intag):
        query_tag = intag
        await self.cursor.execute("SELECT * FROM tag_table WHERE tag_name=? ", [query_tag])
        result = await self.cursor.fetchone()
        if result:
            result_tag = result
            result_tag_id = result_tag

            return result_tag_id
        else:
            return None

    async def create_tag(self, intag):
        query_tag = intag
        await self.cursor.execute("INSERT INTO tag_table (tag_name) VALUES (?)", [intag])
        await self.conn.commit()
        result_tag_id = await self.cursor.lastrowid
        return result_tag_id

    async def map_tag_to_gif(self, tagid, gifid):
        try:
            await self.cursor.execute(
                "INSERT INTO object_tag_mapping VALUES (?,?)", (gifid, tagid)
            )
            await self.conn.commit()
        except Exception as e:
            pass

    async def fetch_gif(self, intag):
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
        result_tag_id = await self.cursor.lastrowid
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
        self.map_tag_to_gif(tagid, urlid)

    async def untag(self, inurl, intag):
        urlid = await self.query_gif(inurl)
        tagid = await self.query_tag(intag)
        if urlid and tagid:
            await self.cursor.execute(
                "DELETE FROM object_tag_mapping  WHERE object_reference = ? AND tag_reference = ?",
                (urlid, tagid),
            )
            await self.conn.commit()

        test_tag_has_url = await self.fetch_gif(intag)

        if not test_tag_has_url:
            await self.cursor.execute("DELETE FROM tag_table WHERE tag_name = ?", (intag,))
            await self.conn.commit()

async def run(loop):
    '''
    conn = await aiosqlite.connect("pythonsqlite.db")
    cur = await conn.cursor()
    await cur.execute("SELECT * FROM tag_table WHERE tag_name=? ", ['woi',])
    row = await cur.fetchone()
    if row:
        print(row)
    else:
        print('nothing')
    '''
    

    async with aiosqlite.connect("pythonsqlite.db", loop=loop) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM tag_table WHERE tag_name=? ", ['woi',])
            r = await cur.fetchall()
            print(r)

    #await cur.close()
    #await conn.close()

    #result_tag_id = await db.fetch_gif(query_in)
    #LOGGER.error("result_tag_id", row)
    '''
    if result_tag_id:
        res = await db.fetch_gif(query_in)
        await print(res)
    else:
        await print("no result")
    '''

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    query_in = input("enter search term: ")
    url_in = input("enter url: ")
    
    #task = asyncio.gather(run())
    try:
        loop.run_until_complete(run(loop))
        #loop.run_forever()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Killed bot.")
    finally:
        #task.cancel()
        loop.close()
