import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment
import base64
import mysecrets
import logging


async def on_request_start(session, context, params):
    logging.getLogger("aiohttp.client").debug(f"Starting request <{params}>")


async def main(loop):
    stream_source = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
    # session = aiohttp.ClientSession()
    logging.basicConfig(level=logging.DEBUG)
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    session = aiohttp.ClientSession(trace_configs=[trace_config])
    headers = {
        "accept": "* / *",
        "accept - encoding": "gzip, deflate, br",
        "accept - language": "ru - RU, ru; q = 0.9, en - US; q = 0.8, en; q = 0.7",
        "cache - control": "no - cache",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }
    async with session.get(stream_source, headers=headers) as response:

        print("started recording")

        # added chunk_count to counter initial data burst of some stations
        chunk_count = 0
        while asyncio.get_event_loop().time() < (start_time + 4):
            chunk = await response.content.read(1024)
            chunk_count += 1
            # print("written chunk ", chunk_count)
            if not chunk:
                break

            recording.write(chunk)
            # some stations send lots of buffered audio on connect which might already be >
            # so we break at 250 chunks. 4s of 256 KBit stream are about 213 chunks
            if chunk_count > 250:
                break

        recording.seek(0)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
