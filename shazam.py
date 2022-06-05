import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment

from aiohttp import ClientSession
import base64
import mysecrets
import sys
shazam_api_key = mysecrets.shazam_api_key


class ShazamApi:
    def __init__(self, loop, api_key ):


        self.api_url = "https://shazam.p.rapidapi.com/"
        self.api_host = "shazam.p.rapidapi.com"
        self.headers = { 
            "content-type": "text/plain",
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": shazam_api_key,
            }


    async def _get(self, streamsource,session = None):
        """
        get from shazam api
        :param query
        :return: API response
        """
        starttime = asyncio.get_event_loop().time()
        recording = BytesIO()

        audio_source = streamsource
        sound = ''
        out = ''
        if session == None:
            session = aiohttp.ClientSession()
        async with session as session:
            try:
                async with session.get(streamsource) as response:
                    print('started recording')
                    while (asyncio.get_event_loop().time() < (starttime + 4)):
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        recording.write(chunk)
                    recording.seek(0)

                    sound = AudioSegment.from_mp3(recording)
                    sound = sound.set_channels(1)
                    sound = sound.set_sample_width(2)
                    sound = sound.set_frame_rate(44100)
            except aiohttp.client_exceptions.ClientConnectorError as e:
                print('there was a ClientConnectorError')
                print(e)
            if sound:
                payload = base64.b64encode(sound.raw_data)
                async with session.post("https://shazam.p.rapidapi.com/songs/v2/detect",data=payload,headers=self.headers) as response:
                    out = await response.json()
            else:
                out = ''
                print('no audio')
            return out


async def loopy(loop):
    n = 1
    while True:
        print('woop',n)
        n += 1
        await asyncio.sleep(1)


async def main(loop):
    
    #audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    #audio_source = 'https://fm.chunt.org/stream'
    audio_source = 'https://doyouworld.out.airtime.pro/doyouworld_a'
    asyncio.ensure_future(loopy(loop))
    api = ShazamApi(loop,shazam_api_key)
    out = await api._get(audio_source)          
    print(out)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))