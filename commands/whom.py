"""
Whom command implementation.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def whom_handler(self, message, cmd, args):
    """Handle !whom command."""
    random_user = (random.choice(message.room.alluserlist)).name
    profile_pic_url = f"https://ust.chatango.com/profileimg/{random_user[0]}/{random_user[1]}/{random_user}/full.jpg"

    await message.channel.send(profile_pic_url)


# Register whom command
register_exact("whom", ["whom"], whom_handler)
