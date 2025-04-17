import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment
import base64
import mysecrets
import logging
import ssl

shazam_api_key = mysecrets.shazam_api_key
print("shazam_api_key: ", shazam_api_key)


async def on_request_start(session, context, params):
    logging.getLogger('aiohttp.client').debug(f'Starting request <{params}>')

class ShazamApi:
    def __init__(self, loop, api_key):
        self.api_url = "https://shazam.p.rapidapi.com/"
        self.api_host = "shazam.p.rapidapi.com"
        self.headers = {
            "content-type": "text/plain",
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": shazam_api_key,
        }

    async def _get(self, stream_source, session=None):
        """
        get from shazam api
        :param stream_source
        :return: API response
        """
        print("running shazam api _get()")
        start_time = asyncio.get_event_loop().time()
        recording = BytesIO()

        audio_source = stream_source
        sound = ""
        out = ""
        print("stream_source: ", stream_source)
        if stream_source == "https://stream.p-node.org/pnode.mp3":
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
        else:
     

            #logging.basicConfig(level=logging.DEBUG)
            #trace_config = aiohttp.TraceConfig()
            #trace_config.on_request_start.append(on_request_start)
            session = aiohttp.ClientSession()
            
        async with session as session:
            try:
                print('attempting connection')
                async with session.get(stream_source) as response:
                    
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
                        # some stations send lots of buffered audio on connect which might already be too much for shazam
                        # so we break at 250 chunks. 4s of 256 KBit stream are about 213 chunks
                        if chunk_count > 250:
                            break

                    recording.seek(0)

                    sound = AudioSegment.from_file(recording)
                    sound = sound.set_channels(1)
                    sound = sound.set_sample_width(2)
                    sound = sound.set_frame_rate(44100)
                 #except aiohttp.client_exceptions.ClientConnectorError as e:
                 #    print("there was a ClientConnectorError")
                 #    print(e)
            except Exception as e:
                print("Error in shazam.py _get")
                print(e)
            if sound:
                payload = base64.b64encode(sound.raw_data)
                async with session.post(
                    "https://shazam.p.rapidapi.com/songs/v2/detect",
                    data=payload,
                    headers=self.headers,
                ) as response:
                    try:
                        out = await response.json()
                    except Exception as e:
                        print(e)
                        print(out)
            else:
                out = ""
                print("no audio")
            return out


async def loopy(loop):
    n = 1
    while True:
        print("woop", n)
        n += 1
        await asyncio.sleep(1)


async def main(loop):
    # audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    # audio_source = 'https://fm.chunt.org/stream'
    #audio_source = "https://doyouworld.out.airtime.pro/doyouworld_a"
    audio_source = "https://kioskradiobxl.out.airtime.pro/kioskradiobxl_a"
    #audio_source = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
    asyncio.ensure_future(loopy(loop))
    #logging.basicConfig(level=logging.DEBUG)
    #trace_config = aiohttp.TraceConfig()
    #trace_config.on_request_start.append(on_request_start)
    api = ShazamApi(loop, shazam_api_key)
    out = await api._get(audio_source)
    print(out)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
