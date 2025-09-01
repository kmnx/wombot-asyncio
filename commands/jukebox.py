"""
Jukebox command implementations.
"""

import helpers.jukebox
from helpers.commands import register_exact, wrapped


@wrapped
async def play_add_handler(self, message, cmd, args):
    """Handle !play and !add commands."""
    import wombot

    # Import MpdSingleton from main module
    mpd = helpers.jukebox.MpdSingleton.get_instance()

    if args:
        # Extract URL from args
        url = args
        if " " in args:
            url = args.split()[0]

        if any(
            domain in url
            for domain in ["soundcloud.com", "mixcloud.com", "nts.live", "bandcamp.com"]
        ):
            await mpd.tracklist.add(url)
            await message.channel.send(f"Added to jukebox: {url}")
        else:
            await message.channel.send(
                "Please provide a valid link from SoundCloud, Mixcloud, NTS, or Bandcamp"
            )
    else:
        await message.channel.send("Please provide a URL to add to the jukebox")


@wrapped
async def queue_handler(self, message, cmd, args):
    """Handle !queue and !tl commands."""
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    try:
        tracklist = await mpd.tracklist.get_tl_tracks()
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
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    try:
        await mpd.playback.next()
        await message.channel.send("Skipped to next track")
    except Exception as e:
        print(f"Error skipping: {e}")
        await message.channel.send("Error skipping track")


@wrapped
async def seek_handler(self, message, cmd, args):
    """Handle !seek command."""
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    if args:
        try:
            position = int(args)
            await mpd.playback.seek(position)
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
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    try:
        # Fast forward by 30 seconds by default
        current_time = await mpd.playback.get_time_position()
        new_position = current_time + 30
        await mpd.playback.seek(new_position)
        await message.channel.send("Fast forwarded 30 seconds")
    except Exception as e:
        print(f"Error fast forwarding: {e}")
        await message.channel.send("Error fast forwarding")


@wrapped
async def rewind_handler(self, message, cmd, args):
    """Handle !rewind and !rw commands."""
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    try:
        # Rewind by 30 seconds by default
        current_time = await mpd.playback.get_time_position()
        new_position = max(0, current_time - 30)
        await mpd.playback.seek(new_position)
        await message.channel.send("Rewound 30 seconds")
    except Exception as e:
        print(f"Error rewinding: {e}")
        await message.channel.send("Error rewinding")


@wrapped
async def clear_handler(self, message, cmd, args):
    """Handle !clear command."""
    import wombot

    mpd = helpers.jukebox.MpdSingleton.get_instance()

    try:
        await mpd.tracklist.clear()
        await message.channel.send("Jukebox queue cleared")
    except Exception as e:
        print(f"Error clearing queue: {e}")
        await message.channel.send("Error clearing queue")


@wrapped
async def juke_handler(self, message, cmd, args):
    """Handle !juke command."""
    import wombot

    jukebox_status_msg = "!juke is down"

    try:
        # Check jukebox status
        mpd = helpers.jukebox.MpdSingleton.get_instance()
        data = await mpd.status()

        if data is not None:
            print(data)
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
