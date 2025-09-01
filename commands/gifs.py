"""
Gif command implementations.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def random_handler(self, message, cmd, args):
    """Handle !random, !rnd, !rand commands."""
    import wombot

    # Get random gif from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db_gif.get_objects_by_tag_name("random")
        if not gif_res:
            # Fallback to any random gif
            gif_res = await self.db_gif.get_random_objects(5)

        if gif_res:
            await message.channel.send(random.choice(gif_res))
        else:
            await message.channel.send("No random content found")
    except Exception as e:
        print(f"Error getting random content: {e}")
        await message.channel.send("Error loading random content")
    finally:
        await connection_pool.close()


@wrapped
async def gif_handler(self, message, cmd, args):
    """Handle !gif, !gift, !dance commands."""
    import wombot

    # Get random gif from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db_gif.get_objects_by_tag_name("dance")
        if not gif_res:
            gif_res = await self.db_gif.get_objects_by_tag_name("gif")
        if not gif_res:
            gif_res = await self.db_gif.get_random_objects(10)

        if gif_res:
            await message.channel.send(random.choice(gif_res))
        else:
            await message.channel.send("No gif content found")
    except Exception as e:
        print(f"Error getting gif content: {e}")
        await message.channel.send("Error loading gif content")
    finally:
        await connection_pool.close()


# Register gif commands
register_exact("random", ["random", "rnd", "rand"], random_handler)
register_exact("gif", ["gif", "gift", "dance"], gif_handler)
