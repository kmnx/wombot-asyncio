"""
Recipe command implementation using Edamam API.
"""

from helpers import edamam
from helpers.commands import register_exact, wrapped


@wrapped
async def scran_handler(self, message, cmd, args):
    """Handle !scran command for recipe suggestions."""
    if args:
        q = args
    else:
        q = "vegetarian"
    
    title, url = await edamam.scran(q)
    if title:
        await message.channel.send("hungry? how about: " + title + " | " + url)


# Register !scran command
register_exact("scran", ["scran"], scran_handler)