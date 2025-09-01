"""
Chunt command implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def chunt_simple_handler(self, message, cmd, args):
    """Handle !chunt command - simple response."""
    await message.channel.send("I'm chuntin")


# Register !chunt command
register_exact("chunt", ["chunt"], chunt_simple_handler)
