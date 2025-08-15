"""
Wombot self-description command implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def wombot_simple_handler(self, message, cmd, args):
    """Handle !wombot command."""
    await message.channel.send(
        "My name is wombot! Call me up using commands "
        + "- for example, hit a !gif for a random gif, "
        + "a !cat for a cat gif, "
        + "or a !fortune for a daily fortune. "
        + "Call up the ChuntFM schedule by hitting !np for Now Playing, "
        + "or !upnext to see what's next xxx"
    )


# Register !wombot command
register_exact("wombot", ["wombot"], wombot_simple_handler)