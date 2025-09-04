import random
from helpers.commands import register_exact, wrapped


@wrapped
async def kiss_handler(self, message, cmd, args):
    """Handle !kiss command."""
    kiss_emojis = ["😘", "💋", "😚", "😙", "💕"]
    emoji = random.choice(kiss_emojis)

    if args:
        await message.channel.send(f"{emoji} *kisses {args}*")
    else:
        await message.channel.send(
            f"{emoji} *sending kisses to {message.user.showname}*"
        )


# Register the kiss command
register_exact("kiss", ["kiss"], kiss_handler)
