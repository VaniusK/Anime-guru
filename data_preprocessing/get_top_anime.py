import pandas as pd
import aiohttp
import asyncio
import time



async def get_top_anime():
    anime_table = pd.DataFrame(data=
    {
        'id': [],
        'title': []
    })
    page = 1
    cnt = 0
    while True:
        async with aiohttp.ClientSession() as session:
            params = [('sfw', 'true'), ('page', page)]
            async with session.get('https://api.jikan.moe/v4/top/anime', params=params) as response:
                json = await response.json()
                if response.status != 200:
                    time.sleep(1)
                    continue
                for anime in json['data']:
                    new_data = pd.DataFrame({
                                   'id': [anime['mal_id']],
                                   'title': [anime['title']]
                               })
                    anime_table = pd.concat([anime_table, new_data], ignore_index=True)
                    cnt += 1
                    if cnt == 1000:
                        anime_table.to_csv("anime_table.csv")
                        return
                if not json['pagination']['has_next_page']:
                    print("Got all anime")
                    anime_table.to_csv("anime_table").csv
                    return

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_top_anime())
