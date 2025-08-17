from urllib.parse import urlparse

from helpers import search_google
from wombot import logger


async def bandcamp_search(artist, title):
    logger.debug("bandcamp_search")

    google_query = artist + " " + title
    ""
    res = await search_google.search(google_query)
    # print(res)
    if res is not None:
        bc_link = res[0]["link"]
        # print(bc_link)
        filters = ["track", "album"]
        parsed = urlparse(bc_link)
        split_path = parsed.path.split("/")
        bc_page_type = split_path[1]
        if any(word in bc_page_type for word in filters):
            bandcamp_result = bc_link
        else:
            bandcamp_result = None

    else:
        bandcamp_result = None

    return bandcamp_result
