"""
Animal command implementations.
"""

import random
from commands import register_exact, wrapped


@wrapped
async def wombat_handler(self, message, cmd, args):
    """Handle !wombat command."""
    wombat_facts = [
        "Wombats have cube-shaped poop! 🧊",
        "Wombats can run up to 25 mph! 🏃",
        "A group of wombats is called a wisdom! 🧠",
        "Wombats have backwards-facing pouches! 👶",
        "Wombats are expert diggers with powerful claws! 🏗️",
        "Wombats can live up to 15 years in the wild! 🎂",
        "The southern hairy-nosed wombat is endangered 😢",
        "Wombats are marsupials, like kangaroos! 🦘",
        "Baby wombats are called joeys! 👶",
        "Wombats have excellent hearing and smell! 👂👃",
    ]
    
    fact = random.choice(wombat_facts)
    await message.channel.send(f"🐹 Wombat fact: {fact}")


@wrapped
async def capybara_handler(self, message, cmd, args):
    """Handle !capybara command."""
    capybara_facts = [
        "Capybaras are the world's largest rodents! 🐭",
        "Capybaras are excellent swimmers! 🏊",
        "Capybaras are very social and live in groups! 👥",
        "Baby capybaras can swim before they can walk! 🏊👶",
        "Capybaras are herbivores and love to graze! 🌱",
        "Capybaras can hold their breath underwater for 5 minutes! 🫧",
        "Capybaras are native to South America! 🌎",
        "Capybaras have webbed feet for swimming! 🦶",
        "Capybaras are crepuscular (most active at dawn/dusk)! 🌅",
        "Capybaras communicate through whistles, clicks, and purrs! 🎵",
    ]
    
    fact = random.choice(capybara_facts)
    await message.channel.send(f"🐹 Capybara fact: {fact}")


@wrapped
async def otter_handler(self, message, cmd, args):
    """Handle !otter command."""
    otter_facts = [
        "Otters hold hands while sleeping to avoid drifting apart! 🤝",
        "Otters have the densest fur in the animal kingdom! 🦫",
        "Sea otters use tools to crack open shellfish! 🔨",
        "Otters have a favorite rock they keep in their armpit! 🪨",
        "Baby otters are called pups! 🐶",
        "Otters can close their nostrils underwater! 👃",
        "A group of otters is called a raft when in water! 🛟",
        "Otters have excellent eyesight both above and below water! 👁️",
        "Otters groom themselves for hours each day! 🧽",
        "River otters can run up to 18 mph on land! 🏃",
    ]
    
    fact = random.choice(otter_facts)
    await message.channel.send(f"🦦 Otter fact: {fact}")


@wrapped
async def quokka_handler(self, message, cmd, args):
    """Handle !quokka command."""
    quokka_facts = [
        "Quokkas are known as the 'world's happiest animal'! 😊",
        "Quokkas are only found on a few islands off Australia! 🏝️",
        "Quokkas are marsupials, like kangaroos! 🦘",
        "Quokkas are herbivores and eat leaves and bark! 🌿",
        "Baby quokkas stay in their mother's pouch for 6 months! 👶",
        "Quokkas are excellent climbers! 🧗",
        "Quokkas are mostly active at night! 🌙",
        "Quokkas can survive without water for long periods! 💧",
        "A group of quokkas is called a shaka! 🤙",
        "Quokkas have become famous for 'selfies' with tourists! 🤳",
    ]
    
    fact = random.choice(quokka_facts)
    await message.channel.send(f"🐨 Quokka fact: {fact}")


# Register all animal commands
register_exact("wombat", ["wombat"], wombat_handler)
register_exact("capybara", ["capybara"], capybara_handler)
register_exact("otter", ["otter"], otter_handler)
register_exact("quokka", ["quokka"], quokka_handler)