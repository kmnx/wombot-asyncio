"""
Help command implementation.
"""

from commands import register_exact, wrapped


@wrapped
async def help_handler(self, message, cmd, args):
    """Handle the !help command."""

    # TODO make this dynamically output all registered commands

    import wombot
    help_message = wombot.help_message
    
    await message.channel.send(help_message)
    await message.room.client.pm.send_message(message.user, help_message)


# Register the command
register_exact("help", ["help"], help_handler)