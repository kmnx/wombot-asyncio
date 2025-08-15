"""
Cannabis-themed command implementations.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def cannabis_handler(self, message, cmd, args):
    """Handle cannabis-themed commands."""
    import wombot
    # Get 420/cannabis gifs from database
    connection_pool = await wombot.create_connection_pool()
    try:
        gif_res = await self.db.get_objects_by_tag_name("420")
        if not gif_res:
            gif_res = await self.db.get_objects_by_tag_name("blaze")
        
        if gif_res:
            await message.channel.send(random.choice(gif_res))
        else:
            await message.channel.send("🌿 Blaze it! 420 🌿")
    except Exception as e:
        print(f"Error getting 420 content: {e}")
        await message.channel.send("🌿 Blaze it! 420 🌿")
    finally:
        await connection_pool.close()


# Register cannabis-themed commands
register_exact("legalize", [
    "legalize", "legalizeit", "legalise", "legalize it", "legalise it", 
    "blaze", "420", "blazeit", "blaze it", "blazin"
], cannabis_handler)