"""
Rollcall command implementation.
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def rollcall_handler(self, message, cmd, args):
    """Handle !rollcall command."""
    if not args or not args[0].isnumeric():
        await message.channel.send(
            "@"
            + message.user.showname
            + ", please add a number between 1 and 8 after the command next time to have the chance of hitting a roll call"
        )
    elif int(args[0]) == random.randint(1, 8):
        await message.channel.send(
            "Congratulations "
            + message.user.showname
            + "! \n"
            + " ".join(["@" + item.name for item in message.room.alluserlist])
        )


# Register rollcall command
register_exact("rollcall", ["rollcall"], rollcall_handler)
