import pandas as pd
import aiohttp
import asyncio
import time
from llm import LLM
import config
from collections import Counter
import json

model = LLM()

all_tags = Counter()
available_tags = set()

def clean_tags(tags):
    tags = tags.split(", ")[:-1]
    tags = [x.lower() for x in tags]
    for i in range(len(tags)):
        if tags[i][0] == ' ':
            tags[i] = tags[i][1:]
        if tags[i][-1] == ' ':
            tags[i] = tags[i][:-1]
    return tags

cnt = 0

async def get_description_by_id(id):
    global available_tags
    global cnt
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.jikan.moe/v4/anime/{id}/full') as response:
                if response.status == 404:
                    return []
                if response.status != 200:
                    time.sleep(0.01)
                    continue
                json = await response.json()
                synopsis = json['data']['synopsis']
                if synopsis == None:
                    synopsis = "Description in unavailable"
                if '[' in synopsis:
                    synopsis = synopsis[:synopsis.find('[')]
                return synopsis

anime_table = pd.read_csv("anime-dataset-2023-with-tags.csv")
if not 'tags' in anime_table.columns:
    anime_table['tags'] = None

k = 50

for i in range(0, len(anime_table)):

    for tag in eval(anime_table.at[i,'tags']):
        tag = tag.replace("\"", "")
        tag = tag.replace("\'", "")
        all_tags[tag] += 1
l = [[all_tags[i], i] for i in all_tags]
l.sort()
l.reverse()
l = l[:150]
print(l)

for i in range(0, len(anime_table)):
    new_tags = []
    for tag in eval(anime_table.at[i,'tags']):
        tag = tag.replace("\"", "")
        tag = tag.replace("\'", "")
        if [all_tags[tag], tag] in l:
            new_tags.append(tag)
    anime_table.at[i, 'tags'] = new_tags
anime_table.to_csv("anime-dataset-2023-with-common-tags.csv")