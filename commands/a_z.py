"""
Simple greeting command implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def a_handler(self, message, cmd, args):
    """Handle !a command - simple greeting."""
    await message.channel.send(f"Hello {message.user.showname}")


@wrapped
async def z_handler(self, message, cmd, args):
    """Handle !z command - simple goodbye."""
    await message.channel.send(f"Goodbye {message.user.showname}")


# Register !a command
register_exact("a", ["a"], a_handler)
# Register !z command
register_exact("z", ["z"], z_handler)
