import datetime
import re
from math import floor

async def parse_future(arg):
    """
    Parse the future
    """

    # try to find timedelta strings
    string_parse = re.findall('([0-9]+)(week|day|hour|minute|second|microseconds)+', arg.lower().strip())

    # @TODO try to find timestamps


    if len(string_parse) > 0:

        delta = datetime.timedelta(**{key: value for value, key in string_parse})

        # get the current time
        now = datetime.datetime.now(datetime.timezone.utc)

        # get the future time
        future = now + delta


    return future


async def format_timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):

    if hasattr(value, 'seconds'):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    seconds_total = seconds

    minutes = int(floor(seconds / 60))
    minutes_total = minutes
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    hours_total = hours
    minutes -= hours * 60

    days = int(floor(hours / 24))
    days_total = days
    hours -= days * 24

    years = int(floor(days / 365))
    years_total = years
    days -= years * 365

    return time_format.format(**{
        'seconds': seconds,
        'seconds2': str(seconds).zfill(2),
        'minutes': minutes,
        'minutes2': str(minutes).zfill(2),
        'hours': hours,
        'hours2': str(hours).zfill(2),
        'days': days,
        'years': years,
        'seconds_total': seconds_total,
        'minutes_total': minutes_total,
        'hours_total': hours_total,
        'days_total': days_total,
        'years_total': years_total,
    })