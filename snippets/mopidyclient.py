import asyncio
import logging

from mopidy_asyncio_client import MopidyClient


logging.basicConfig()
logging.getLogger("mopidy_asyncio_client").setLevel(logging.DEBUG)


async def playback_started_handler(data):
    """Callback function, called when the playback started."""
    print(data)


async def all_events_handler(event, data):
    """Callback function; catch-all function."""
    print(event, data)


async def main_context_manager():

    async with MopidyClient(host="139.177.181.183") as mopidy:

        mopidy.bind("track_playback_started", playback_started_handler)
        mopidy.bind("*", all_events_handler)

        # Your program's logic:
        # await mopidy.playback.play()
        while True:
            await asyncio.sleep(1)


async def main_plain():

    mopidy = await MopidyClient().connect()

    mopidy.bind("track_playback_started", playback_started_handler)
    mopidy.bind("*", all_events_handler)

    # Your program's logic:
    await mopidy.playback.play()
    while True:
        await asyncio.sleep(1)

    await mopidy.disconnect()  # close connection implicit


# Either ...
# asyncio.run(main_context_manager())
# ... or
# asyncio.run(main_plain())
