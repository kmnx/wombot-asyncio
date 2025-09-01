"""
Sandwich command implementation.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def sandwich_handler(self, message, cmd, args):
    """Handle !sandwich command."""
    import wombot

    # Get sandwich and bbb gifs
    connection_pool = await wombot.create_connection_pool()
    try:
        # First get sandwich gif
        sandwich_res = await self.db.get_objects_by_tag_name("sandwich")
        if sandwich_res:
            await message.channel.send(random.choice(sandwich_res))

            # Then get random bbb gifs
            bbb_res = await self.db.get_objects_by_tag_name("bbb")
            if bbb_res:
                # Send a few random bbb gifs
                selected_bbb = random.choices(bbb_res, k=min(3, len(bbb_res)))
                for gif in selected_bbb:
                    await message.channel.send(gif)
        else:
            await message.channel.send("🥪 Sandwich time!")
    except Exception as e:
        print(f"Error getting sandwich content: {e}")
        await message.channel.send("🥪 Sandwich time!")
    finally:
        await connection_pool.close()


# Register sandwich command
register_exact("sandwich", ["sandwich"], sandwich_handler)
