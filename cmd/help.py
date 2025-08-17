"""
Help command implementation.
"""

from helpers.commands import register_exact, wrapped


@wrapped
async def help_handler(self, message, cmd, args):
    """Handle the !help command."""

    # TODO make this dynamically output all registered commands

    import wombot
    help_message = help_message
    
    await message.channel.send(help_message)
    await message.room.client.pm.send_message(message.user, help_message)


# Register the command
register_exact("help", ["help"], help_handler)
help_message = (
    "commands: \r \r "
    + "!id1 to shazam chunt1 \r!idnts1 for NTS1 \r!idyourfavouritestation for your favourite station \r \r"
    + "!fortune (your daily fortune)  \r \r "
    + "!shoutout [username]  \r "
    + "!b2b for some random random gifs \r !rnd for even more random gifs \r"
    + "gifs curated by bigbunnybrer, oscmal, and others \r \r"
    + "keep chuntin!"
)
