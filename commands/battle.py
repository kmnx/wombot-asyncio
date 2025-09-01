"""
Battle command implementation.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def battle_handler(self, message, cmd, args):
    """Handle !battle command."""
    random_user1 = (random.choice(message.room.alluserlist)).name
    random_user2 = (random.choice(message.room.alluserlist)).name
    profile_pic_url1 = f"https://ust.chatango.com/profileimg/{random_user1[0]}/{random_user1[1]}/{random_user1}/full.jpg"
    profile_pic_url2 = f"https://ust.chatango.com/profileimg/{random_user2[0]}/{random_user2[1]}/{random_user2}/full.jpg"
    gif_vs = "https://media4.giphy.com/media/saFoLCfgRajNm/giphy.gif"
    await message.channel.send(profile_pic_url1 + " " + gif_vs + " " + profile_pic_url2)


# Register battle command
register_exact("battle", ["battle"], battle_handler)
