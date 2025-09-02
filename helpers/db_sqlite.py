import aiosqlite


class AsyncDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    async def open(self):
        self.conn = await aiosqlite.connect(self.db_path)

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def execute(self, query, params=None):
        params = params or ()
        async with self.conn.execute(query, params) as cursor:
            await self.conn.commit()
            return await cursor.fetchall()

    async def execute_write(self, query, params=None):
        params = params or ()
        await self.conn.execute(query, params)
        await self.conn.commit()
