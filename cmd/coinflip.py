"""
Coinflip command implementation.
"""

import random
from commands import register_exact, wrapped


@wrapped
async def coinflip_handler(self, message, cmd, args):
    """Handle !coinflip command."""
    coinflip_result = "Heads" if random.choice([0, 1]) == 1 else "Tails"

    if args:
        await message.channel.send(
            "@"
            + message.user.showname
            + " asked: "
            + args
            + " - coin flip result is: "
            + coinflip_result
        )
    else:
        await message.channel.send(
            "coin flip result is: " + coinflip_result
        )


# Register coinflip command
register_exact("coinflip", ["coinflip"], coinflip_handler)