import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment
import numpy as np
import radioactivity

# from madmom.audio.signal import Signal
# from madmom.features.tempo import TempoEstimationProcessor
import aubio
import ssl


async def get_bpm(station):
    print(f"get_bpm called with station: {station}")
    if station == "nts1":
        stream_url = "https://stream-relay-geo.ntslive.net/stream"
        station_name = "NTS1"
        match = True
    elif station == "nts2":
        stream_url = "https://stream-relay-geo.ntslive.net/stream2"
        station_name = "NTS2"
        match = True
    elif station == "doyou":
        stream_url = "https://doyouworld.out.airtime.pro/doyouworld_a"
        station_name = "DoYou"
        match = True
    elif station == "chunt1":
        stream_url = "https://fm.chunt.org/stream"
        station_name = "ChuntFM"
        match = True
    elif station == "chunt2":
        stream_url = "https://fm.chunt.org/stream2"
        station_name = "Juke"

        match = True
    elif station in ["1", "ch1", "chu1", "chunt1", "chunt"]:
        stream_url = "https://fm.chunt.org/stream"
        station_name = "ChuntFM"
        match = True
    elif station in ["2", "ch2", "chu2", "chunt2", "juke"]:
        stream_url = "https://fm.chunt.org/stream2"
        station_name = "Juke"
        match = True

    elif station == "soho":
        stream_url = "https://sohoradiomusic.doughunt.co.uk:8010/128mp3"
        match = True
    elif station == "alhara":
        stream_url = "https://n13.radiojar.com/78cxy6wkxtzuv?1708984512=&rj-tok=AAABjedzXYAAkdrS5yt-8kMFEA&rj-ttl=5"
        match = True
    elif station == "sharedfrequencies":
        stream_url = "https://sharedfrequencies.out.airtime.pro/sharedfrequencies_a"
        match = True
    else:
        ra_stations = await radioactivity.get_station_list()
        print("wtf")
        ra_station_names = list(ra_stations.keys())

        if station in ra_station_names:
            station_name = station
            match = True
        # try to guess which station is meant
        else:
            print("trying to guess station")
            station_name = [
                item
                for item in ra_station_names
                if station in item.lower() or station in item.upper()
            ]

            # if more than station has particular matches, return an error message
            if station_name is not None:

                print(f"it's not none: station_name: {station_name}")
                if isinstance(station_name, list) and len(station_name) > 1:
                    return None
                elif isinstance(station_name, list) and len(station_name) == 0:
                    return None
                else:
                    match = True
                    station_name = station_name[0]
                    print(f"found station_name: {station_name}")
            if match:
                print(f"station_name matched: {station_name}")
                id_station = ra_stations[station_name]
                # for all stations urls for the given station, run the shazam api and append results to the message
                for stream in id_station["stream_url"]:
                    stream_name = stream[0]
                    if stream_name == "station":
                        stream_name = ""
                    stream_url = stream[1]

    # station could be identified, let's go
    if match:
        bpm = 0
        bpm = await main(stream_url=stream_url)
        return station_name, bpm
    else:
        return None


async def record_audio_snippet(stream_url, duration_sec=6):
    recording = BytesIO()
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.get(stream_url, ssl=ssl_context) as response:
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() < (start_time + duration_sec):
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                recording.write(chunk)
    recording.seek(0)
    return recording


def madmom_detect_bpm(audio_bytes):
    proc = TempoEstimationProcessor(fps=100)
    bpm = proc(audio_bytes)[0][0]  # Returns (bpm, strength)
    return bpm


def detect_bpm(audio_bytes):
    # Load audio with pydub, convert to mono, 44.1kHz, 16-bit
    sound = AudioSegment.from_file(audio_bytes)
    sound = sound.set_channels(1).set_frame_rate(44100).set_sample_width(2)
    # Convert to numpy array for librosa
    samples = np.array(sound.get_array_of_samples()).astype(np.float32) / 32768.0
    # Use HPSS to separate percussive elements
    y_harmonic, y_percussive = librosa.effects.hpss(samples)
    # Use percussive part for beat tracking
    tempo, _ = librosa.beat.beat_track(y=y_percussive, sr=44100)
    print(f"Detected tempo: {tempo} BPM")
    return tempo


def aubio_detect_bpm(audio_bytes):
    sound = AudioSegment.from_file(audio_bytes)
    sound = sound.set_channels(1).set_frame_rate(44100).set_sample_width(2)
    samples = np.array(sound.get_array_of_samples()).astype(np.float32) / 32768.0

    win_s = 1024
    hop_s = 512
    tempo_obj = aubio.tempo("default", win_s, hop_s, 44100)
    beats = []
    for i in range(0, len(samples), hop_s):
        block = samples[i : i + hop_s]
        if len(block) < hop_s:
            block = np.pad(block, (0, hop_s - len(block)))
        is_beat = tempo_obj(block)
        if is_beat:
            beats.append(tempo_obj.get_bpm())
    if beats:
        return float(np.median(beats))
    return 0.0


async def main(stream_url=None):
    print("got a request for bpm")
    print(f"stream_url: {stream_url}")
    if stream_url is None:
        stream_url = "https://stream-relay-geo.ntslive.net/stream"
    print("Recording snippet...")
    snippet = await record_audio_snippet(stream_url)
    print("Detecting BPM...")
    bpm = aubio_detect_bpm(snippet)
    # Ensure bpm is a Python float, not a NumPy scalar or array
    if hasattr(bpm, "item"):
        bpm = bpm.item()
    # return print(f"Estimated BPM: {bpm:.2f}")

    return bpm


if __name__ == "__main__":
    asyncio.run(main())
