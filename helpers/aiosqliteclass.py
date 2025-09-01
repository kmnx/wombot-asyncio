import asyncio
import aiosqlite
import logging
import random
import os 
logger = logging.getLogger(__name__)


async def create_conn():
    db = Sqlite3Class()
    await db._init()
    return db


class Sqlite3Class:
    # self.cursor.row_factory = lambda cursor, row: row[0]

    def __init__(self, db_name=None):
        if db_name is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_name = os.path.join(base_dir, "data", "database_gifs.db")
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    async def _init(self):

        self.conn = await aiosqlite.connect(self.db_name)
        self.cursor = await self.conn.cursor()
        # Create tables if they don't exist
        await self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS object_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_name TEXT UNIQUE
            )
        """
        )
        await self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tag_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            )
        """
        )
        await self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS object_tag_mapping (
                object_reference INTEGER,
                tag_reference INTEGER,
                FOREIGN KEY(object_reference) REFERENCES object_table(id),
                FOREIGN KEY(tag_reference) REFERENCES tag_table(id)
            )
        """
        )
        await self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_table (
                object_id INTEGER PRIMARY KEY,
                object_name TEXT UNIQUE
            )
        """
        )
        await self.conn.commit()

    async def _close(self):
        await self.conn.close()

    async def get_tag_id_from_tag(self, intag):
        await self.cursor.execute(
            "SELECT id FROM tag_table WHERE tag_name=? ", (intag,)
        )
        result = await self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    async def get_object_id_from_object(self, inurl):
        """
        Retrieves the object ID from the object table based on the given object URL.

        Args:
            inurl (str): The URL of the object.

        Returns:
            dict or None: A dictionary containing the object details if found, or None if not found.
        """
        print("query_url", inurl)
        await self.cursor.execute(
            "SELECT id FROM object_table WHERE object_name=? ", (inurl,)
        )
        result = await self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    async def create_tag(self, intag):
        await self.cursor.execute(
            "INSERT INTO tag_table (tag_name) VALUES (?)", (intag,)
        )
        await self.conn.commit()
        result_tag_id = self.cursor.lastrowid
        return result_tag_id

    async def create_object(self, inurl):
        await self.cursor.execute(
            "INSERT INTO object_table (object_name) VALUES (?)", (inurl,)
        )
        await self.conn.commit()
        result_tag_id = self.cursor.lastrowid
        return result_tag_id

    async def create_mapping(self, tagid, gifid):
        try:
            await self.cursor.execute(
                "INSERT INTO object_tag_mapping VALUES (?,?)", (gifid, tagid)
            )
            await self.conn.commit()
        except Exception as e:
            print(e)
            pass

    async def tag(self, inurl, intag):
        urlid = await self.get_object_id_from_object(inurl)
        print("tag urlid", urlid)
        if not urlid:
            urlid = await self.create_object(inurl)

        tagid = await self.get_tag_id_from_tag(intag)
        print("tag tagid", tagid)
        if not tagid:
            tagid = await self.create_tag(intag)

        await self.create_mapping(tagid, urlid)

    async def get_objects_by_tag_name(self, intag):
        await self.cursor.execute(
            """
            SELECT object_name
            FROM object_tag_mapping
            JOIN object_table ON object_reference = object_table.id
            JOIN tag_table ON tag_reference = tag_table.id
            WHERE tag_name = ?
            AND object_table.id NOT IN (SELECT object_id FROM blocked_table)
            """,
            (intag,),
        )
        object_list = []
        result = await self.cursor.fetchall()
        if result:
            for item in result:
                if item:
                    object_list.append(item[0])
        return object_list

    async def get_tag_names_by_object_name(self, inurl):
        await self.cursor.execute(
            "SELECT tag_name from object_tag_mapping JOIN tag_table ON tag_reference = tag_table.id JOIN object_table ON object_reference = object_table.id WHERE object_name = ?",
            (inurl,),
        )

        result = await self.cursor.fetchall()
        tag_names = []
        if result:
            for item in result:
                tag_names.append(item[0])
        return tag_names

    async def get_tag_names_by_object_id(self, gif_id):
        await self.cursor.execute(
            "SELECT tag_name FROM object_tag_mapping "
            "JOIN tag_table ON tag_reference = tag_table.id "
            "WHERE object_reference = ?",
            (gif_id,),
        )
        result = await self.cursor.fetchall()
        return result

    async def untag(self, inurl, intag):
        print("untagging....")
        urlid = await self.get_object_id_from_object(inurl)
        tagid = await self.get_tag_id_from_tag(intag)
        print(urlid)
        print(tagid)
        if urlid and tagid:
            await self.remove_mapping_by_ids(urlid, tagid)

        test_tag_has_object = await self.get_objects_by_tag_name(intag)
        print(test_tag_has_object)

        if not test_tag_has_object:
            await self.cursor.execute(
                "DELETE FROM tag_table WHERE tag_name = ?", (intag,)
            )
            await self.conn.commit()

        test_object_has_tags = await self.get_tag_names_by_object_name(inurl)
        print(test_object_has_tags)

        if not test_object_has_tags:
            await self.remove_object_by_object_id(urlid)

    async def untag_simple(self, in_string):
        tag_id = await self.get_tag_id_from_tag(in_string)
        object_id = await self.get_object_id_from_object(in_string)
        if object_id and tag_id:
            return None
        else:
            if tag_id:
                mapped_objects = await self.get_object_ids_by_tag_id(tag_id)
                if mapped_objects:
                    if len(mapped_objects) > 1:
                        return None
                    else:
                        object_id = mapped_objects[0][0]
                        await self.remove_mapping_by_ids(object_id, tag_id)
                        await self.conn.commit()
                        await self.remove_tag_by_tag_id(tag_id)
                        mapped_tags = await self.get_tag_ids_by_object_id(object_id)
                        if not mapped_tags:
                            await self.remove_object_by_object_id(object_id)
                        return 1
            elif object_id:
                mapped_tags = await self.get_tag_ids_by_object_id(object_id)
                if mapped_tags:
                    if len(mapped_tags) > 1:
                        return None
                    else:
                        tag_id = mapped_tags[0][1]
                        await self.remove_mapping_by_ids(object_id, tag_id)
                        await self.conn.commit()
                        await self.remove_object_by_object_id(object_id)
                        mapped_objects = await self.get_object_ids_by_tag_id(tag_id)
                        if not mapped_objects:
                            await self.remove_tag_by_tag_id(tag_id)
                        return 1

    async def untag_by_tag_id(self, tag_id):
        tuples = await self.get_object_ids_by_tag_id(tag_id)
        if tuples:
            if len(tuples) > 1:
                pass
            else:
                object_id = tuples[0][0]

                print(object_id)
                print(tag_id)
                if object_id and tag_id:
                    await self.remove_mapping_by_ids(object_id, tag_id)
                    await self.conn.commit()
                    await self.remove_tag_by_tag_id(tag_id)

                test_object_has_tags = await self.get_tag_ids_by_object_id(object_id)
                print(test_object_has_tags)

                if not test_object_has_tags:
                    await self.remove_object_by_object_id(object_id)

    async def untag_by_tag_name(self, tag_name):
        tuples = await self.get_objects_by_tag_name(tag_name)
        if tuples:
            if len(tuples) > 1:
                pass
            else:
                object_id = tuples[0][0]
                tag_id = tuples[0][1]
                print(object_id)
                print(tag_id)
                if object_id and tag_id:
                    await self.remove_mapping_by_ids(object_id, tag_id)
                    await self.remove_tag_by_tag_id(tag_id)

                test_object_has_tags = await self.get_tag_names_by_object_id(object_id)
                print(test_object_has_tags)

                if not test_object_has_tags:
                    await self.remove_object_by_object_id(object_id)

    async def untag_by_object_id_and_object_data(self, object_id, object_data):
        tag_ids = await self.get_tag_ids_by_object_id(object_id)
        object_data_from_db = await self.get_object_by_object_id(object_id)

        if object_data_from_db is None:
            print("object not found")
            print(object_id)
            print(object_data)
        else:
            if object_data_from_db[1].strip().strip("'") == object_data:
                print(object_data)
                # print(object_id)
                # print(tag_ids)
                await self.remove_object_by_object_id(object_id)
                if object_id and tag_ids:
                    for tag_id in tag_ids:
                        tag_name = await self.get_tag_name_by_tag_id(tag_id[1])

                        print(tag_name[1])
                        # print(tag_id[1])
                        await self.remove_mapping_by_ids(object_id, tag_id[1])
                        await self.conn.commit()
                        test_tag_has_objects = await self.get_object_ids_by_tag_id(
                            tag_id[1]
                        )
                        # print(test_tag_has_objects)

                        if test_tag_has_objects:
                            pass
                        else:
                            print("dead:", tag_name[1])
                            await self.remove_tag_by_tag_id(tag_id[1])
                            print(tag_name)
            else:
                print("object data does not match")
                print(object_data_from_db)
                print(object_data)

    async def info(self, in_string):
        resulting_tags = []
        resulting_urls = []
        object_result = await self.get_objects_by_tag_name(in_string)

        for object in object_result:
            if object:
                resulting_urls.append(object)
        tag_result = await self.get_tag_names_by_object_name(in_string)
        for tag in tag_result:
            if tag:
                resulting_tags.append(tag)
        print(resulting_tags, resulting_urls)
        return resulting_urls, resulting_tags

    async def get_tag_ids_by_object_id(self, object_id):
        """
        Retrieves the tag IDs associated with the given object ID.

        Args:
            object_id (int): The ID of the object.

        Returns:
            tuples of (object_id,tag_id) or None.
        """
        await self.cursor.execute(
            "SELECT * FROM object_tag_mapping WHERE object_reference=?", (object_id,)
        )
        result = await self.cursor.fetchall()
        if result:
            return result
        else:
            return None

    async def get_object_ids_by_tag_id(self, tag_id):
        await self.cursor.execute(
            "SELECT object_reference FROM object_tag_mapping WHERE tag_reference=?",
            (tag_id,),
        )
        result = await self.cursor.fetchall()
        if result:
            return result
        else:
            return None

    async def get_object_by_object_id(self, object_id):
        await self.cursor.execute(
            "SELECT object_name FROM object_table WHERE id=?", (object_id,)
        )
        result = await self.cursor.fetchone()
        if result:
            return result
        else:
            return None

    async def get_tag_name_by_tag_id(self, tag_id):
        await self.cursor.execute(
            "SELECT tag_name FROM tag_table WHERE id=?", (tag_id,)
        )
        result = await self.cursor.fetchone()
        if result:
            return result
        else:
            return None

    async def remove_tag_by_tag_id(self, tag_id):
        await self.cursor.execute("DELETE FROM tag_table WHERE id = ?", (tag_id,))
        await self.conn.commit()

    async def remove_object_by_object_id(self, object_id):
        await self.cursor.execute("DELETE FROM object_table WHERE id = ?", (object_id,))
        await self.conn.commit()

    async def remove_mapping_by_ids(self, object_id, tag_id):
        await self.cursor.execute(
            "DELETE FROM object_tag_mapping  WHERE object_reference = ? AND tag_reference = ?",
            (
                object_id,
                tag_id,
            ),
        )
        await self.conn.commit()

    async def get_random_unblocked_gif(self):
        await self.cursor.execute(
            """
            SELECT object_name FROM object_table
            WHERE id NOT IN (SELECT object_id FROM blocked_table)
            """
        )
        results = await self.cursor.fetchall()
        if results:
            return random.choice(results)[0]
        else:
            return None

    async def block_object(self, inurl):
        urlid = await self.get_object_id_from_object(inurl)
        if urlid:
            await self.cursor.execute(
                "INSERT OR IGNORE INTO blocked_table (object_id, object_name) VALUES (?, ?)",
                (urlid, inurl),
            )
            await self.conn.commit()

    async def unblock_object(self, inurl):
        urlid = await self.get_object_id_from_object(inurl)
        if urlid:
            await self.cursor.execute(
                "DELETE FROM blocked_table WHERE object_id = ?", (urlid,)
            )
            await self.conn.commit()


async def run():
    db = Sqlite3Class()
    await db._init()
    gif = await db.get_random_unblocked_gif()
    if gif:
        print("Random gif:", gif)
    else:
        print("No unblocked gifs found.")
    await db._close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] Exiting.")
