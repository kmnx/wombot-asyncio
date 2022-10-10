import datetime
import re
from math import floor

async def parse_future(arg):
    """
    Parse the future
    """

    print ('trying to parse future: ' + arg)

    arg = str(arg)

    try:
        # try to find timedelta strings
        string_parse = re.findall('([0-9]+)((?:week|day|hour|minute|second|microsecond)s*)+', arg.lower().strip())
    except Exception as e:
        print('Could not parse future: ' + str(e))
        raise e


    print(string_parse)
    # @TODO try to find timestamps


    if len(string_parse) > 0:

        args_dict = [(val, key) if key.endswith('s') else (val, key+'s') for val, key in string_parse]

        try:
            delta = datetime.timedelta(**{key: int(value) for value, key in args_dict})
        except Exception as e:
            print('Could not parse future: ' + str(e))
            raise e

        # get the current time
        now = datetime.datetime.now(datetime.timezone.utc)

        # get the future time
        future = now + delta


    return future


async def format_timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):

    if isinstance(value, datetime.timedelta):
        seconds = value.total_seconds()
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