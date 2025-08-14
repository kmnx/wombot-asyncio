"""
Count command implementation.
"""

from commands import register_exact, wrapped


@wrapped
async def count_handler(self, message, cmd, args):
    """Handle the !count command."""
    print("user count", self._room.usercount)


# Register the command
register_exact("count", ["count"], count_handler)