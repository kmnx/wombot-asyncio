"""
Goth command implementation.
"""

import random
from commands import register_exact, wrapped


@wrapped
async def goth_handler(self, message, cmd, args):
    """Handle !goth command."""
    import wombot
    # Get random goth gif from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db.get_objects_by_tag_name("goth")
        if gif_res:
            await message.channel.send(random.choice(gif_res))
        else:
            await message.channel.send("No goth content found 🦇")
    except Exception as e:
        print(f"Error getting goth content: {e}")
        await message.channel.send("Error loading goth content")
    finally:
        await connection_pool.close()


# Register goth command
register_exact("goth", ["goth"], goth_handler)