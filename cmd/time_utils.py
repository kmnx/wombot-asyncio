"""
Time and date utility command implementations.
"""

from datetime import datetime, timezone
from helpers.commands import register_exact, wrapped
from typing import List, Dict
import zoneinfo

if not zoneinfo.available_timezones():
    import tzdata


@wrapped
async def timeis_handler(self, message, cmd, args):
    """Handle !timeis and !time commands."""

    date_format = "%I:%M %p"
    utc_now = datetime.now(timezone.utc)

    # Name to print & IANA time zone
    places = {
        "Amsterdam": zoneinfo.ZoneInfo("Europe/Amsterdam"),
        "Bali": zoneinfo.ZoneInfo("Asia/Makassar"),
        "London": zoneinfo.ZoneInfo("Europe/London"),
        "Lisboa": zoneinfo.ZoneInfo("Europe/Lisbon"),
        "New York": zoneinfo.ZoneInfo("America/New_York"),
        "Palanga": zoneinfo.ZoneInfo("Europe/Vilnius"),
        "San Diego": zoneinfo.ZoneInfo("America/Los_Angeles"),
        "São Paulo": zoneinfo.ZoneInfo("America/Sao_Paulo"),
        "Sydney": zoneinfo.ZoneInfo("Australia/Sydney"),
        "Texas": zoneinfo.ZoneInfo("America/Chicago"),
        "Tōkyō": zoneinfo.ZoneInfo("Asia/Tokyo"),
        "Reykjavík": zoneinfo.ZoneInfo("Iceland"),
    }

    local_datetimes: List[Dict[str, datetime]] = []
    for place, local_zone in places.items():
        local_time = utc_now.astimezone(local_zone)
        local_datetimes.append(
            {
                "place": place,
                "time": local_time,
            }
        )

    local_datetimes.sort(key=lambda d: (d["time"].hour, d["time"].min))

    local_strings = [
        f'{n["place"]} {n["time"].strftime(date_format)}'
        for n in local_datetimes
    ]

    msg_str = " | ".join(local_strings)

    await message.channel.send(msg_str)


@wrapped
async def days_handler(self, message, cmd, args):
    """Handle !days and !date commands."""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    await message.channel.send(f"Today is: {current_date}")


# Register time utility commands
register_exact("timeis", ["timeis", "time"], timeis_handler)
register_exact("days", ["days", "date"], days_handler)