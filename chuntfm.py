import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment
from pydub.silence import detect_silence, detect_nonsilent



async def chuntfm_live():

    starttime = asyncio.get_event_loop().time()
    recording = BytesIO()

    audio_source = 'https://fm.chunt.org/stream'
    sound = ''

    session = aiohttp.ClientSession()
    starttime = asyncio.get_event_loop().time()

    async with session as session:
        async with session.get(audio_source) as response:
            print('started recording')
            while (asyncio.get_event_loop().time() < (starttime + 1)):
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                recording.write(chunk)
            recording.seek(0)

    sound = AudioSegment.from_mp3(recording)

    silence_check = detect_silence(sound, min_silence_len=900, silence_thresh=-30)

    silence_list = [len(range(silence[0], silence[1]))>900 for silence in silence_check]

    # if all detected silences ar elonger than 900 miliseconds
    if len(silence_list) > 0 and all(silence_list):
        return False
    else:
        return True


