"""
Coinflip command implementation.
"""

import random
from helpers.commands import register_exact, wrapped

eightball = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]

@wrapped
async def eightball_handler(self, message, cmd, args):
    """Handle !8ball command."""
    eightball_result = random.choice(eightball)

    if args:
        await message.channel.send(
            "@"
            + message.user.showname
            + " asked: "
            + args
            + " - 8 ball says:  "
            + eightball_result
        )
    else:
        await message.channel.send(eightball_result)


# Register coinflip command
register_exact("8ball", ["8ball"], eightball_handler)
