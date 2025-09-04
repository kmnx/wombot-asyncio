import aiohttp
import asyncio
import json
import socket
import mysecrets


async def get_chuntfm_status(status_url="https://chunt.org/chuntfm.json"):

    # read in json from url
    try:
        async with aiohttp.ClientSession() as session:
            thisproxy = mysecrets.proxy
            async with session.get(status_url, proxy=thisproxy) as response:
                json_response = await response.read()
        cfm_status = json_response.decode("utf-8")
        cfm_status = json.loads(cfm_status)
        print(cfm_status)
        return cfm_status
    except Exception as e:
        print(e)
        print("what")
        return None


async def main(loop):
    status = await get_chuntfm_status()
    print(status)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
