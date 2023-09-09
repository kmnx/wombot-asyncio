import aiohttp

from datetime import datetime, timezone, timedelta

# import datetime
import json
import pytz
from dateutil import parser

apis = {
    "nts1": "https://www.nts.live/api/v2/radio/schedule/1",
    "nts2": "https://www.nts.live/api/v2/radio/schedule/2",
}


async def get_now_playing(station):
    today = datetime.now().date()
    print(today)
    time_now = datetime.now(timezone.utc)
    api_url = apis.get(station)
    session = aiohttp.ClientSession()
    async with session as s:
        async with s.get(api_url) as resp:
            data = await resp.json()

    if "nts.live/api" in api_url:
        data = data["results"]
        sched = []
        tz = pytz.timezone("Europe/London")
        now_playing = ""
        for result in data:
            if result.get("date") == str(today):
                sched = result.get("broadcasts")
                for broadcast in sched:
                    start_time = parser.parse(broadcast.get("start_timestamp"))
                    if start_time <= time_now:
                        end_time = parser.parse(broadcast.get("end_timestamp"))
                        if end_time >= time_now:
                            now_playing = broadcast.get("broadcast_title").strip()
                            break
                break
        print(now_playing)
        return now_playing


async def get_schedule(api_url):
    """
    Get schedule from an api

    Returns:
    a list object containing the schedule of the station with one dict per show with entries
        start: start time of the show as a datetime object
        end: end time of the show as a datetime object
        title: title of the show as a string
    """

    # open api url and pull data
    session = aiohttp.ClientSession()
    async with session as s:
        async with s.get(api_url) as resp:
            data = await resp.json()
        # response = await s.get(api_url)

    # data = json.loads(await response.read())

    if "nts.live/api" in api_url:
        data = data["results"]
        sched = []

        for day in data:
            for show in day.get("broadcasts", []):
                sched.append(
                    {
                        "start": datetime.strptime(
                            show.get("start_timestamp"), "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        "end": datetime.strptime(
                            show.get("end_timestamp"), "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        "title": show.get("broadcast_title").strip(),
                    }
                )

    if data is not None:
        return sched
    else:
        raise Exception("Could not get station schedule.")


async def subset_schedule(sched, time, future_hours=12):
    """
    Function to subset a schedule
    time must be supplied as a datetime object

    schedule: list of dicts containing the schedule
    time: datetime object with tz info
    future_hours: number of hours to look ahead
    """

    if time.tzinfo is None:
        raise Exception(
            "Time must be supplied as a datetime object with timezone information."
        )

    schedule_subset = [
        show
        for show in sched
        if show["start"] > time and show["start"] < time + timedelta(hours=future_hours)
    ]

    return schedule_subset


async def pprint_schedule(sched, string=True):
    """
    Pretty print a schedule by date
    """

    pretty_schedule = "All times in local station time!\n"

    date = None

    for show in sched:
        if date is None or date != show["start"].date():
            add_date = True
        else:
            add_date = False

        date = show["start"].date()

        if add_date:
            pretty_schedule += "\n" + str(date) + "\n\n"

        pretty_schedule += (
            "{} - {} {}".format(
                datetime.strftime(show["start"], "%H:%M"),
                datetime.strftime(show["end"], "%H:%M"),
                show["title"],
            )
            + "\n"
        )

    if string:
        return pretty_schedule
    else:
        print(pretty_schedule)


if __name__ == "__main__":
    import asyncio
    import sys

    loop = asyncio.get_event_loop()
    if len(sys.argv) > 1:
        station = sys.argv[1]
    else:
        station = "nts1"
    loop.run_until_complete(get_now_playing("nts1"))
    loop.run_until_complete(get_now_playing("nts2"))
