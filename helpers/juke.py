import asyncio
import logging
from os import environ

from helpers.timing import convert_to_time
from mopidy_asyncio_client import MopidyClient

logger = logging.getLogger(__name__)

# new Implementation 

class Jukebox:
    def __init__(self, host):
        self.host = host
        self.mpd = MopidyClient(host=self.host)


    def display_progress(self, track_position, track_length):
        position_str = convert_to_time(track_position)
        length_str = convert_to_time(track_length)

        percentage = int((track_position / track_length) * 100)
        progress_bar_length = 10
        progress_bar = "#" * (percentage // (100 // progress_bar_length))
        remaining_space = "." * (progress_bar_length - len(progress_bar))

        print(
            f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%"
        )
        return f"at [{position_str}] of [{length_str}] [{progress_bar}{remaining_space}] {percentage}%"


    async def jukebox_status(self):
        #mpd = MpdSingleton.get_instance()
        data = None
        print("trying to get mpd data")
        try:
            data = await self.mpd.playback.get_current_track()
        except Exception as e:
            print("exception in np")
            print(e)
            jukebox_status_msg = "!juke is down"

        if data is not None:
            print(data)
            jukebox_status_msg = " !juke is playing"

        else:
            print("no mpd data")
            url = ""
            jukebox_status_msg = ""
        return jukebox_status_msg


    async def now_playing_jukebox(self,return_type=None):
        #mpd = MpdSingleton.get_instance()
        chu2_np_formatted = ""
        chu2_np_raw = None

        # anything on chu2?
        data = None
        print("trying to get mpd data")
        try:
            data = await self.mpd.playback.get_current_track()
            track_position = await self.mpd.playback.get_time_position()
        except Exception as e:
            print("exception in np")
            print(e)

        # print(data)

        if data is not None:
            print(data)
            track_length = data["length"]
            progress_bar = self.display_progress(track_position, track_length)
            if "__model__" in data:
                if data["uri"].startswith("mixcloud"):
                    uri = data["uri"]
                    url = uri.replace("mixcloud:track:", "https://www.mixcloud.com")

                elif data["uri"].startswith("soundcloud"):
                    url = data["comment"]
                elif data["uri"].startswith("bandcamp"):
                    comment = data["comment"]
                    url = comment.replace("URL: ", "")
                else:
                    url = ""
                chu2_np_raw = url
                chu2_np_formatted = (
                    " https://fm.chunt.org/stream2 jukebox now playing: "
                    + url
                    + " "
                    + progress_bar
                )

        else:
            print("no mpd data")
            url = ""
            chu2_np_formatted = "jukebox is empty. !add a link from sc,mc,bc or nts!"

        if return_type == "formatted":
            return chu2_np_formatted
        elif return_type == "raw":
            return chu2_np_raw


    async def playback_started_handler(self, data):
        logger.debug("playback_started_handler")
        #from wombot import BotSingleton

        #bot = BotSingleton.get_instance()
        """Callback function, called when the playback started."""
        print(data)
        print(self.rooms)  # ok
        main_room = environ["wombotmainroom"]
        my_room = self.get_room(main_room)
        # print(my_room) # ok
        if data["tl_track"]["track"]["uri"].startswith("soundcloud"):
            url = data["tl_track"]["track"]["comment"]
        elif data["tl_track"]["track"]["uri"].startswith("mixcloud"):
            uri = data["tl_track"]["track"]["uri"]
            url = uri.replace("mixcloud:uris:", "https://www.mixcloud.com")
        else:
            url = data["tl_track"]["track"]["name"]
        msg = "https://fm.chunt.org/stream2 jukebox now playing: " + url
        await my_room.send_message(msg)


    async def all_events_handler(self, event, data):
        logger.debug("all_events_handler")

        """Callback function; catch-all function."""
        print(event, data)
        if event == "tracklist_changed":
            print(data)


    async def mpd_context_manager(self):
        logger.debug("mpd_context_manager")

        try:
            async with self.mpd as mopidy:
                mopidy.bind("track_playback_started", self.playback_started_handler)
                mopidy.bind("*", self.all_events_handler)
                await mopidy.tracklist.set_consume(True)

                # Your program's logic:
                # await mopidy.playback.play()
                while True:
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(e)
            print(e)

    def start(self):
        # Launch the context manager as a background task
        self._mpd_task = asyncio.create_task(self.mpd_context_manager())
        return self._mpd_task



