"""
Animal command implementations.
"""

import random
from helpers.commands import register_exact, wrapped
from data import data_pics_wombat, data_pics_capybara, data_pics_otter, data_pics_quokka

@wrapped
async def wombat_handler(self, message, cmd, args):
    """Handle !wombat command."""
    await message.channel.send(random.choice(data_pics_wombat.pics))

@wrapped
async def capybara_handler(self, message, cmd, args):
    """Handle !capybara command."""
    await message.channel.send(random.choice(data_pics_capybara.pics))

@wrapped
async def otter_handler(self, message, cmd, args):
    """Handle !otter command."""
    await message.channel.send(random.choice(data_pics_otter.pics))


@wrapped
async def quokka_handler(self, message, cmd, args):
    """Handle !quokka command."""
    print("quokka")
    if message.room.name != "<PM>":
    await message.channel.send(random.choice(data_pics_quokka.pics))


# Register all animal commands
register_exact("wombat", ["wombat"], wombat_handler)
register_exact("capybara", ["capybara"], capybara_handler)
register_exact("otter", ["otter"], otter_handler)
register_exact("quokka", ["quokka"], quokka_handler)
