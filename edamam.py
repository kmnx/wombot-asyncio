import mysecrets
from aiohttp import ClientSession
import asyncio


async def scran(q):
    url = "https://api.edamam.com/api/recipes/v2"
    params = {
        "type": "public",
        "app_id": mysecrets.edamam_app_id,
        "app_key": mysecrets.edamam_app_key,
        "random": "true",
        "q": q,
    }
    session = ClientSession(trust_env=True)
    try:
        async with session as s:
            async with s.get(url=url, params=params) as r:
                jsonresp = await r.json()
                recipe_name = jsonresp["hits"][0]["recipe"]["label"]
                recipe_url = jsonresp["hits"][0]["recipe"]["url"]
    except Exception as e:
        print(e)
    return recipe_name, recipe_url


async def main(loop):
    thisscran = await scran("vegetarian")
    print(thisscran)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
