import random
from datetime import date, timedelta
import re

from data import data_text_anniversaries as anniversaries
from helpers.commands import wrapped, register_regex


@wrapped
async def anniversary_handler(self, message, cmd, args):
    """
    Prints the date + info of given an #number
    """

    zero_day = date(2022, 3, 14)

    match = re.match(r"^chunt#(\d{3,4})$", cmd)
    if not match:
        await message.channel.send(
            "Invalid command format. Please use chunt#NNN or chunt#NNNN."
        )
        return
    this_number = int(match.group(1))
    anni_date = zero_day + timedelta(days=this_number)
    days_differnt = (anni_date - date.today()).days

    anni_str = anni_date.strftime("%Y/%m/%d")
    msg_str = f"CHUNT {this_number:03}"

    # dict - contains know dates
    if this_number in anniversaries.numbers:
        suffix = anniversaries.numbers[this_number]
    else:
        suffix = None

    # what is the tense?
    if days_differnt == 0:
        future = None
        msg_str += f" is today, celebrate with us!"
    else:
        if days_differnt >= 1:
            future = True
            msg_str += f" is happening on {anni_str}"
        else:
            future = False
            msg_str += f" happend on {anni_str}"

    # add generic suffixes
    if suffix is None:

        coinflip = random.choice([0, 1])
        if this_number % 100 == 0 and future is True:
            suffix = random.choice(anniversaries.round_future)
        else:
            if coinflip:
                if future is True:
                    suffix = random.choice(anniversaries.generic_future)
                elif future is False:
                    suffix = random.choice(anniversaries.generic_past)

    if suffix:
        msg_str += f": {suffix}"

    await message.channel.send(msg_str)


# Register the anniversary command

register_regex("chunt#", r"^chunt#(\d{3,4})$", anniversary_handler)
