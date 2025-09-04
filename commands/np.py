"""
np (now playing) command implementation.
"""

from aiohttp import ClientSession
from pytz import timezone
from helpers.commands import register_exact, wrapped
import datetime
from helpers.now_playing import now_playing


@wrapped
async def np_handler(bot, message, cmd, args):
    """Handle the !np command."""
    np_result = await now_playing(bot)
    print("now what")


# Register the command
register_exact("np", ["np"], np_handler)
