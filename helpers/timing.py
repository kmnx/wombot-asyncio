import re
from datetime import datetime

import pytz


def get_uk_timezone_label():
    uk_tz = pytz.timezone("Europe/London")
    now = datetime.now(uk_tz)
    if now.dst():
        return "BST"
    else:
        return "GMT"


def validate_and_convert_to_milliseconds(seektime):
    # Regular expression to match the format HH:MM:SS, HH:MM, or MM
    pattern = r"^(\d{1,2}):(\d{1,2}):(\d{1,2})$|^(\d{1,2}):(\d{1,2})$|^(\d{1,2})$"

    # Check if the input matches the pattern
    match = re.match(pattern, seektime)

    if match:
        # Extract hours, minutes, and seconds from the matched groups
        groups = match.groups()
        hours = int(groups[0]) if groups[0] else int(groups[3]) if groups[3] else 0
        minutes = (
            int(groups[1])
            if groups[1]
            else int(groups[4]) if groups[4] else int(groups[5]) if groups[5] else 0
        )
        seconds = int(groups[2]) if groups[2] else 0

        # If single digit, add leading zero
        hours = str(hours).zfill(2)
        minutes = str(minutes).zfill(2)
        seconds = str(seconds).zfill(2)

        # Convert to milliseconds
        total_milliseconds = (
            int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        ) * 1000
        return total_milliseconds
    else:
        return None


def convert_to_time(milliseconds):
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def convert_utc_to_london(utctime):
    naive_time = datetime.strptime(utctime, "%Y-%m-%d %H:%M:%S")
    utc_time = naive_time.replace(tzinfo=pytz.UTC)
    london_tz = pytz.timezone("Europe/London")
    london_time = utc_time.astimezone(london_tz)
    string_time = str(london_time)
    less_time = string_time.split(" ")[1].split(":")
    hours_minutes = str(less_time[0]) + ":" + str(less_time[1])

    return hours_minutes
