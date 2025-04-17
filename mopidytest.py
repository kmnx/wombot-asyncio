import asyncio
import logging

from mopidy_asyncio_client import MopidyClient


logging.basicConfig()
logging.getLogger('mopidy_asyncio_client').setLevel(logging.DEBUG)


async def playback_started_handler(data):
    """Callback function, called when the playback started."""
    print(data)


async def all_events_handler(event, data):
    """Callback function; catch-all function."""
    print(event, data)


async def main():
    mopidy = MopidyClient(host='139.177.181.183')  # Create the client instance
    #mopidy = MopidyClient(host='what')
    try:
        await mopidy.connect()  # Explicitly connect to the Mopidy server

        mopidy.bind('track_playback_started', playback_started_handler)
        mopidy.bind('*', all_events_handler)

        # Your program's logic:
        await mopidy.playback.play()
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await mopidy.disconnect()  # Ensure the connection is closed


# Run the main function
asyncio.run(main())