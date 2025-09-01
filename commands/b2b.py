"""
B2B (back-to-back) command implementations.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def b2b_handler(self, message, cmd, args):
    """Handle !b2b command."""
    import wombot

    # Get random b2b gifs from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db_gif.get_objects_by_tag_name("bbb")
        if gif_res:
            # Send multiple gifs for b2b effect
            selected_gifs = random.choices(gif_res, k=min(3, len(gif_res)))
            for gif in selected_gifs:
                await message.channel.send(gif)
        else:
            await message.channel.send("No b2b content found")
    except Exception as e:
        print(f"Error getting b2b content: {e}")
        await message.channel.send("Error loading b2b content")
    finally:
        await connection_pool.close()


@wrapped
async def b2b2b_handler(self, message, cmd, args):
    """Handle !b2b2b, !bbbb, !b3b commands."""
    import wombot

    # Even more b2b action
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db_gif.get_objects_by_tag_name("b2b")
        if gif_res:
            # Send even more gifs for b2b2b effect
            selected_gifs = random.choices(gif_res, k=min(5, len(gif_res)))
            for gif in selected_gifs:
                await message.channel.send(gif)
        else:
            await message.channel.send("No b2b content found")
    except Exception as e:
        print(f"Error getting b2b content: {e}")
        await message.channel.send("Error loading b2b content")
    finally:
        await connection_pool.close()


@wrapped
async def bbb_handler(self, message, cmd, args):
    """Handle !bbb, !bigb commands."""
    import wombot

    # Get bbb gifs from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db_gif.get_objects_by_tag_name("bbb")
        if gif_res:
            await message.channel.send(random.choice(gif_res))
        else:
            await message.channel.send("No bbb content found")
    except Exception as e:
        print(f"Error getting bbb content: {e}")
        await message.channel.send("Error loading bbb content")
    finally:
        await connection_pool.close()


# Register b2b commands
register_exact("b2b", ["b2b"], b2b_handler)
register_exact("b2b2b", ["b2b2b", "bbbb", "b3b"], b2b2b_handler)
register_exact("bbb", ["bbb", "bigb"], bbb_handler)
