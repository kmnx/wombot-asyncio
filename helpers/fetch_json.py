from aiohttp import ClientSession


async def fetch_json(url):
    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                return await response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        # return {"error": str(e)}
        return None
