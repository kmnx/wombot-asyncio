"""
Jukebox command implementations.
"""

# import helpers.jukebox
import json
from urllib.parse import urlparse
from aiohttp import ClientSession
import bs4
from helpers.commands import register_exact, wrapped


@wrapped
async def play_add_handler(self, message, cmd, args):
    """Handle !play and !add commands."""

    playback_state = await self.mpd.mpd.playback.get_state()
    schemes = await self.mpd.mpd.core.get_uri_schemes()
    # print(schemes)
    if args:
        splitargs = args.split(" ")
        url = splitargs[0]

        stripped_url = url.strip().lstrip().rstrip()
        url = stripped_url
        results = ""
        added = ""

        if url.startswith("https://www.nts.live"):
            async with ClientSession() as s:
                r = await s.get(url)
                html = await r.read()
                soup = bs4.BeautifulSoup(html, features="lxml")
                buttons = soup.find("button", {"data-src": True})
                source = buttons.get("data-src")
                url = source

        if url.startswith("https://rinse.fm/episodes/"):
            async with ClientSession() as s:
                r = await s.get(url)
                html = await r.read()
                soup = bs4.BeautifulSoup(html, features="lxml")
                res = soup.find_all("script", type="application/json")
                jo = json.loads(res[0].string)
                url = jo["props"]["pageProps"]["entry"]["fileUrl"]

        parsed = urlparse(url)
        mypath = parsed.path

        if url.startswith("https://www.mixcloud.com"):
            uri = "mixcloud:track:" + mypath
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)

        elif url.startswith("https://m.mixcloud.com"):
            uri = "mixcloud:track:" + mypath
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)

        elif url.startswith("https://soundcloud.com/"):
            uri = "sc:" + url
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)

        elif url.startswith("https://m.soundcloud.com/"):
            nurl = url.replace("https://m.", "https://")
            uri = "sc:" + nurl
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)

        elif "bandcamp" in url:
            uri = "bandcamp:" + url
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)

        if url.startswith("https://www.youtube.com/watch"):
            """added = ""
            # uri = "yt:" + url
            # yt seems very broken, causes "wrong stream type" somewhere in liquidsoap/icecast/mopidy chain
            await message.channel.send(
                "jukebox can currently add links from mixcloud,soundcloud,bandcamp,nts"
            )"""
            uri = "yt:" + url
            search_uri = []
            search_uri.append(uri)
            added = await self.mpd.mpd.tracklist.add(uris=search_uri)
        if added:
            if "__model__" in added[0]:
                await message.channel.send("jukebox successfully added " + url)
            elif "ValidationError" in added:
                await message.channel.send(
                    "could not add "
                    + url
                    + " to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts"
                )
        else:
            await message.channel.send(
                "could not add "
                + url
                + " to jukebox. supported links: mixcloud,soundcloud,bandcamp,nts"
            )

        if playback_state != "playing":
            top_slice = await self.mpd.mpd.tracklist.slice(0, 1)

            if top_slice is not None:
                tlid = top_slice[0]["tlid"]
                playback_state = await self.mpd.mpd.playback.get_state()
                print("Playback state before play():", playback_state)
                await self.mpd.mpd.playback.play()
                playback_state = await self.mpd.mpd.playback.get_state()
                print("Playback state after play():", playback_state)
        else:
            print("should be playing")

        if results:
            print(results)
    else:
        await message.channel.send("Please provide a URL to add to the jukebox")


@wrapped
async def queue_handler(self, message, cmd, args):
    """Handle !queue and !tl commands."""

    try:
        tracklist = await self.mpd.mpd.tracklist.get_tl_tracks()
        i = 0
        small_list = []

        for item in tracklist:
            i += 1
            track_name = item["track"].get("name", item["track"]["uri"])
            small_list.append(track_name)

        tiny_list = small_list[:3]

        if i == 0:
            msg = "jukebox is not playing anything. !add a link from sc,mc,bc or nts!"
        else:
            msg = f"{i} tracks in jukebox queue. "
            for item in tiny_list:
                msg += " | " + item

        await message.channel.send(msg)

    except Exception as e:
        print(f"Error getting queue: {e}")
        await message.channel.send("Error getting jukebox queue")


@wrapped
async def skip_handler(self, message, cmd, args):
    """Handle !skip command."""

    try:
        await self.mpd.playback.next()
        await message.channel.send("Skipped to next track")
    except Exception as e:
        print(f"Error skipping: {e}")
        await message.channel.send("Error skipping track")


@wrapped
async def seek_handler(self, message, cmd, args):
    """Handle !seek command."""

    if args:
        try:
            position = int(args)
            await self.mpd.playback.seek(position)
            await message.channel.send(f"Seeked to {position} seconds")
        except ValueError:
            await message.channel.send("Please provide a valid number of seconds")
        except Exception as e:
            print(f"Error seeking: {e}")
            await message.channel.send("Error seeking")
    else:
        await message.channel.send("Please specify position in seconds")


@wrapped
async def ff_handler(self, message, cmd, args):
    """Handle !ff and !fastforward commands."""

    try:
        # Fast forward by 30 seconds by default
        current_time = await self.mpd.playback.get_time_position()
        new_position = current_time + 30
        await self.mpd.playback.seek(new_position)
        await message.channel.send("Fast forwarded 30 seconds")
    except Exception as e:
        print(f"Error fast forwarding: {e}")
        await message.channel.send("Error fast forwarding")


@wrapped
async def rewind_handler(self, message, cmd, args):
    """Handle !rewind and !rw commands."""

    try:
        # Rewind by 30 seconds by default
        current_time = await self.mpd.playback.get_time_position()
        new_position = max(0, current_time - 30)
        await self.mpd.playback.seek(new_position)
        await message.channel.send("Rewound 30 seconds")
    except Exception as e:
        print(f"Error rewinding: {e}")
        await message.channel.send("Error rewinding")


@wrapped
async def clear_handler(self, message, cmd, args):
    """Handle !clear command."""

    try:
        await self.mpd.tracklist.clear()
        await message.channel.send("Jukebox queue cleared")
    except Exception as e:
        print(f"Error clearing queue: {e}")
        await message.channel.send("Error clearing queue")


@wrapped
async def juke_handler(self, message, cmd, args):
    """Handle !juke command."""

    jukebox_status_msg = "!juke is down"

    try:
        # Check jukebox status
        data = await self.mpd.jukebox_status()
        if data is not None:
            jukebox_status_msg = " !juke is playing"
        else:
            print("no mpd data")

        if jukebox_status_msg == " !juke is playing":
            jukebox_status_msg = "https://fm.chunt.org/stream2 jukebox commands: !add url !skip !np \r accepts links from mixcloud,soundcloud,nts"

        await message.channel.send(jukebox_status_msg)

    except Exception as e:
        print(f"Error checking juke status: {e}")
        await message.channel.send(jukebox_status_msg)


# Register all jukebox commands
register_exact("play", ["play", "add"], play_add_handler)
register_exact("queue", ["queue", "tl"], queue_handler)
register_exact("skip", ["skip"], skip_handler)
register_exact("seek", ["seek"], seek_handler)
register_exact("ff", ["ff", "fastforward"], ff_handler)
register_exact("rewind", ["rewind", "rw"], rewind_handler)
register_exact("clear", ["clear"], clear_handler)
register_exact("juke", ["juke"], juke_handler)
