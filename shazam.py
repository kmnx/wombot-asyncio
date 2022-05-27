import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment

from aiohttp import ClientSession
import base64

import sys
shazam_api_key = "41934f7a32msh48132dd2d353798p1a99d4jsn817d99d65fe3"



class ShazamApi:
    def __init__(self, loop, api_key ):


        self.api_url = "https://shazam.p.rapidapi.com/"
        self.api_host = "shazam.p.rapidapi.com"
        self.headers = { 
            "content-type": "text/plain",
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": shazam_api_key,
            }
        
        self.session = ClientSession(trust_env=True)

    async def _get(self, streamsource):
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

        async with self.session as session:
            try:
                async with session.get(streamsource) as response:
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
            except aiohttp.ClientConnectorError as e:
                print('there was a ClientConnectorError')
                print(e)
            if sound:
                payload = base64.b64encode(sound.raw_data)
                #async with aiohttp.ClientSession() as session:
                async with session.post("https://shazam.p.rapidapi.com/songs/v2/detect",data=payload,headers=self.headers) as response:
                    out = await response.json()
            else:
                print('there was no sound')
            return out





async def main(loop):
    
    #audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    #audio_source = 'https://fm.chunt.org/stream'
    audio_source = 'https://doyouworld.out.airtime.pro/doyouworld_a'
    
    api = ShazamApi(loop,shazam_api_key)

    async with api.session as session:
        out = await api._get(audio_source)
                

    print(out)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))