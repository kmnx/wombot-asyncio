import aiohttp
import asyncio 

async def get_location_from_ip(ip):
    url = f"http://ip-api.com/json/{ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if data["status"] == "success":
                return {
                    "city": data.get("city"),
                    "country": data.get("country"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                }
            else:
                return None
            
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python locationguess.py <ip>")
    else:
        ip = sys.argv[1]
        location = asyncio.run(get_location_from_ip(ip))
        if location:
            print(f"Location for IP {ip}: {location}")
        else:
            print(f"Could not find location for IP {ip}")