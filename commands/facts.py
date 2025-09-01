"""
Facts command implementations (properly translated from original wombot.py).
"""

import random
from helpers.commands import register_exact, wrapped


@wrapped
async def funfact_handler(self, message, cmd, args):
    """Handle !funfact and !fact commands."""
    import wombot

    random_fact = random.choice(wombot.facts)["text"]
    await message.channel.send(
        "your random fact, "
        + message.user.showname
        + " : "
        + random_fact.replace(".", "").lower()
    )


@wrapped
async def chuntfact_handler(self, message, cmd, args):
    """Handle !chuntfact and !cact commands."""
    import wombot
    import nltk

    random_fact = random.choice(wombot.facts)["text"]
    random_user = (random.choice(message.room.alluserlist)).name
    tokens = nltk.word_tokenize(random_fact)
    tagged = [[token, tag] for (token, tag) in nltk.pos_tag(tokens)]
    nn_idx = []
    nns_idx = []
    nnp_idx = []
    for i, [token, tag] in enumerate(tagged):
        if tag == "VBD":
            tagged[i][0] = "chunted"
        elif tag == "NN":
            nn_idx.append(i)
        elif tag == "NNS":
            nns_idx.append(i)
        elif tag == "NNP":
            nnp_idx.append(i)
    try:
        tagged[random.choice(nn_idx)][0] = "chunt"
    except IndexError:
        pass
    try:
        tagged[random.choice(nns_idx)][0] = "chunts"
    except IndexError:
        pass
    try:
        tagged[random.choice(nnp_idx)][0] = random_user
    except IndexError:
        pass
    chunted_fact = " ".join([token[0] for token in tagged])
    await message.channel.send(
        "your chunted random fact, "
        + message.user.showname
        + " : "
        + chunted_fact.replace(".", "").lower()
    )


# Register facts commands
register_exact("funfact", ["funfact", "fact"], funfact_handler)
register_exact("chuntfact", ["chuntfact", "cact"], chuntfact_handler)
