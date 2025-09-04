from datetime import datetime,timezone
from aiohttp import ClientSession
from helpers.fetch_json import fetch_json


async def now_playing(bot):
    live_status = ""
    chu1_np = ""
    chu2_np = ""
    # is someone connected?
    live_json = await fetch_json("https://chunt.org/live.json")
    if live_json["live"] == True:
        live_status = "source"
    else:
        print(live_json)
    # is something scheduled?
    chu1_scheduled = None
    schedule_json = await fetch_json("https://chunt.org/schedule.json")
    if schedule_json:
        print("got schedule_json")
        time_now = datetime.now(timezone.utc)
        print("time_now: ", time_now)
        for show in schedule_json:
            start_time = datetime.fromisoformat(show["startTimestamp"])
            end_time = datetime.fromisoformat(show["endTimestamp"])
            # print("start_time: ", start_time)
            if start_time < time_now:
                if end_time > time_now:
                    print(show)
                    chu1_scheduled = show["title"]
    

    # someone is connected
    if live_status.startswith("source"):
        if chu1_scheduled:
            chu1_np = "LIVE NOW: " + chu1_scheduled
        else:
            chu1_np = "LIVE NOW: unscheduled livestream w/ anon1111"

    # no one is connected
    else:
        # get current restream info
        chu_restream_json = await fetch_json("https://chunt.org/restream.json")
        if chu_restream_json:
                print(chu_restream_json)
                # is someone supposed to be connected?
                if chu1_scheduled is not None:
                    print("someone is scheduled")
                    if chu_restream_json["current"]["show_date"] is None:
                        chu_restream_json["current"]["show_date"] = ""
                    chu1_np = (
                        "scheduled but offline: "
                        + chu1_scheduled
                        + " | "
                        + "RESTREAM: "
                        + chu_restream_json["current"]["show_title"]
                        + " @ "
                        + chu_restream_json["current"]["show_date"]
                    )
                # no one is scheduled, just show restream info
                else:
                    print("no one is scheduled")
                    if chu_restream_json["current"]["show_date"] is None:
                        chu_restream_json["current"]["show_date"] = ""
                    chu1_np = (
                        "RESTREAM: "
                        + chu_restream_json["current"]["show_title"]
                        + " @ "
                        + chu_restream_json["current"]["show_date"]
                    )


    # anything on chu2?
    chu2_np = await bot.jukebox_status()
    if chu1_np == "":
        chu1_np = "i think chunt.org might be broken"

    if chu2_np:
        chu1_np = chu1_np + " | " + chu2_np


    return chu1_np