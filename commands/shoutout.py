import random
from helpers.commands import register_exact, wrapped


@wrapped
async def shoutout_handler(self, message, cmd, args):
    """Handle !shoutout, !shout, !out commands."""

    shout_start = [
        "out to you, ",
        "out to the absolute legend ",
        "much love out to ",
        "out to the amazing ",
        "out to the inimitable",
    ]

    shout_end = ["😘", "❤️", "💙", "*h*", "<3"]

    if args:
        splitargs = args.split(" ")
        if args.startswith("@"):
            for arg in splitargs:
                print("arg ", arg)
                if arg.startswith("@"):
                    await message.channel.send(
                        random.choice(shout_start)
                        + " "
                        + arg
                        + " ! "
                        + random.choice(shout_end)
                    )

    else:

        await message.channel.send(
            "Please provide a user to shout out (e.g., !shoutout @username)."
        )


# Register the shoutout command
register_exact("shoutout", ["shoutout", "shout", "out"], shoutout_handler)
