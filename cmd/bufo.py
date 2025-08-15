"""
Ben UFO sound command implementations.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def bufo_handler(self, message, cmd, args):
    """Handle !whatdoesthatmean, !benufo, !bufo commands."""
    try:
        await message.channel.send(
            "https://f001.backblazeb2.com/file/chuntongo/ben_ufo-whatdoesthatmean.mp3"
        )
    except Exception as e:
        print(f"Error playing Ben UFO sound: {e}")
        await message.channel.send("🛸 What does that mean? 🛸")


# Register Ben UFO commands
register_exact("whatdoesthatmean", ["whatdoesthatmean", "benufo", "bufo"], bufo_handler)