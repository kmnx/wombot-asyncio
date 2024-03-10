import asyncio
from mopidy_asyncio_client import MopidyClient
import logging
from os import environ

class JukeboxManager:
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.mpd_task = self.loop.create_task(self.start_mpd_context_manager(self.loop))

    async def start_mpd_context_manager(self, loop):
        self.mpd = MopidyClient(host="139.177.181.183")
        return self.mpd_context_manager(self.mpd)

    async def playback_started_handler(self, data):
        logging.debug("playback_started_handler")
        print(data)
        print(self.bot.rooms)  # ok
        main_room = environ["wombotmainroom"]
        my_room = self.bot.get_room(main_room)
        if data["tl_track"]["track"]["uri"].startswith("soundcloud"):
            url = data["tl_track"]["track"]["comment"]
        elif data["tl_track"]["track"]["uri"].startswith("mixcloud"):
            uri = data["tl_track"]["track"]["uri"]
            url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")
        else:
            url = data["tl_track"]["track"]["name"]
        msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
        await my_room.send_message(msg)

    async def all_events_handler(self, event, data):
        logging.debug("all_events_handler")

    async def mpd_context_manager(self, mpd):
        logging.debug("mpd_context_manager")

        async with mpd as mopidy:
            mopidy.bind("track_playback_started", self.playback_started_handler)
            mopidy.bind("*", self.all_events_handler)
            await mpd.tracklist.set_consume(True)

            # Your program's logic:
            # await mopidy.playback.play()
            while True:
                await asyncio.sleep(1)

    async def playback_started_handler(self, data):
        logging.debug("playback_started_handler")

        """Callback function, called when the playback started."""
        print(data)
        print(self.bot.rooms)  # ok
        main_room = environ["wombotmainroom"]
        my_room = self.bot.get_room(main_room)
        # print(my_room) # ok
        if data["tl_track"]["track"]["uri"].startswith("soundcloud"):
            url = data["tl_track"]["track"]["comment"]
        elif data["tl_track"]["track"]["uri"].startswith("mixcloud"):
            uri = data["tl_track"]["track"]["uri"]
            url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")
        else:
            url = data["tl_track"]["track"]["name"]
        msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
        await my_room.send_message(msg)