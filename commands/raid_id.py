"""
Raid and ID prefix commands implementation.
"""

import asyncio

import helpers.shazam
from helpers.commands import register_startswith, delete_unless_pm


async def raid_or_id_handler(self, message, cmd, args):
    """Handle commands that start with 'raid' or 'id'."""
    await delete_unless_pm(message)

    newcmd = cmd
    if cmd.startswith("raid"):
        newcmd = cmd[4:]
    elif cmd.startswith("id"):
        newcmd = cmd[2:]

    import wombot

    asyncio.ensure_future(helpers.shazam.raid(self, message, newcmd))


# Register the startswith patterns
register_startswith("raid", raid_or_id_handler)
register_startswith("id", raid_or_id_handler)
