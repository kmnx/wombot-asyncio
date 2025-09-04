"""
ChuntFM people command implementations.
"""

from datetime import date

from helpers.commands import register_exact, wrapped


@wrapped
async def ronfret_handler(self, message, cmd, args):
    """Handle !ronfret command."""
    ronfret_date = date(2024, 4, 13)
    days_left = str((ronfret_date - date.today()).days)
    await message.channel.send(
        "13/14 April 2024 weekend for Ronfret 2024 in Lisboa. Only "
        + days_left
        + " days left, you should probably have acted fast by now!"
    )


@wrapped
async def chavalon_handler(self, message, cmd, args):
    """Handle !chavalon command."""
    chavalon_date = date(2024, 9, 21)
    days_left = str((chavalon_date - date.today()).days)
    await message.channel.send(
        "CHUNT922 @ AVALON CAFE: 21 SEPTEMBER : only "
        + days_left
        + " days left, act fast!"
    )


# Register ChuntFM people commands
register_exact("ronfret", ["ronfret"], ronfret_handler)
register_exact("chavalon", ["chavalon"], chavalon_handler)
