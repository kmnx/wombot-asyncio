"""
Bandcamp Game command implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def bcg_handler(self, message, cmd, args):
    """Handle !bcg command."""
    await message.channel.send(
        "the Bandcamp Game: Click on what's playing, click a buyer, "
        "click something they bought that you like the look of and !add the track to queue"
    )


# Register !bcg command
register_exact("bcg", ["bcg"], bcg_handler)
