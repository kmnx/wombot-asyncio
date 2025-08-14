"""
Text manipulation command implementations.
"""

import html
from commands import register_exact, wrapped


@wrapped
async def say_handler(self, message, cmd, args):
    """Handle !say command."""
    if not args:
        await message.channel.send("What should I say?")
    else:
        # Clean HTML and limit length
        clean_message = html.escape(args[:200])
        await message.channel.send(clean_message)


# Register text manipulation commands
register_exact("say", ["say"], say_handler)
