"""
Fortune command implementations (properly translated from original wombot.py).
"""

import random
from helpers.commands import register_exact, wrapped

from data import data_txt_fortunes as fortunes


@wrapped
async def fortune_handler(self, message, cmd, args):
    """Handle !fortune command."""

    coinflip = random.choice([0, 1])

    if (coinflip == 0) or (message.user.showname == "yungdale"):
        await message.channel.send(
            "your fortune, "
            + message.user.showname
            + " : "
            + (random.choice(fortunes.fortunecookie)).replace(".", "").lower()
        )
    else:
        import nltk

        sentence = random.choice(fortunes.fortunecookie)
        tokens = nltk.word_tokenize(sentence)
        tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
        nn_idx = []
        nns_idx = []
        for i, [token, tag] in enumerate(tagged):
            if tag == "VBD":
                tagged[i][0] = "chunted"
            elif tag == "NN":
                nn_idx.append(i)
            elif tag == "NNS":
                nns_idx.append(i)
        try:
            tagged[random.choice(nn_idx)][0] = "chunt"
        except IndexError:
            pass
        try:
            tagged[random.choice(nns_idx)][0] = "chunts"
        except IndexError:
            pass
        cfortune = " ".join([token[0] for token in tagged])
        await message.channel.send(
            "your chunted fortune, "
            + message.user.showname
            + " : "
            + cfortune.replace(".", "").lower()
        )


@wrapped
async def cfortune_handler(self, message, cmd, args):
    """Handle !cfortune command."""
    import nltk

    sentence = random.choice(fortunes.fortunecookie)
    tokens = nltk.word_tokenize(sentence)
    tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
    nn_idx = []
    nns_idx = []
    for i, [token, tag] in enumerate(tagged):
        if tag == "VBD":
            tagged[i][0] = "chunted"
        elif tag == "NN":
            nn_idx.append(i)
        elif tag == "NNS":
            nns_idx.append(i)
    try:
        tagged[random.choice(nn_idx)][0] = "chunt"
    except IndexError:
        pass
    try:
        tagged[random.choice(nns_idx)][0] = "chunts"
    except IndexError:
        pass
    cfortune = " ".join([token[0] for token in tagged])
    await message.channel.send(
        "your chunted fortune, "
        + message.user.showname
        + " : "
        + cfortune.replace(".", "").lower()
    )


@wrapped
async def normalfortune_handler(self, message, cmd, args):
    """Handle !normalfortune command."""

    await message.channel.send(
        "your fortune, "
        + message.user.showname
        + " : "
        + (random.choice(fortunes.fortunecookie)).replace(".", "").lower()
    )


@wrapped
async def boshtune_handler(self, message, cmd, args):
    """Handle !boshtune command."""
    import nltk

    sentence = random.choice(fortunes.fortunecookie)
    tokens = nltk.word_tokenize(sentence)
    tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
    nn_idx = []
    nns_idx = []
    for i, [token, tag] in enumerate(tagged):
        if tag == "VBD":
            tagged[i][0] = "boshed"
        elif tag == "NN":
            nn_idx.append(i)
        elif tag == "NNS":
            nns_idx.append(i)
    try:
        tagged[random.choice(nn_idx)][0] = "bosh"
    except IndexError:
        pass
    try:
        tagged[random.choice(nns_idx)][0] = "boshs"
    except IndexError:
        pass
    cfortune = " ".join([token[0] for token in tagged])
    await message.channel.send(
        "your boshed fortune, "
        + message.user.showname
        + " : "
        + cfortune.replace(".", "").lower()
    )


# Register fortune commands only
register_exact("fortune", ["fortune"], fortune_handler)
register_exact("cfortune", ["cfortune"], cfortune_handler)
register_exact("normalfortune", ["normalfortune"], normalfortune_handler)
register_exact("boshtune", ["boshtune"], boshtune_handler)
