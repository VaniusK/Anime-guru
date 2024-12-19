from typing import List, Dict, Any
import pandas as pd
import json

from llm import LLM

model = LLM()

anime_table = pd.read_csv("anime-dataset-2023-with-common-tags.csv")

def merge_anime_based_on_request(anime_lists: List[List[int]], request: str) -> List[int]:
    merged_list = []
    for anime_list in anime_lists:
        merged_list += anime_list
    json_list = []
    for anime_id in merged_list:
        json_list.append({"ID": anime_id,
                          "Title": anime_table.at[anime_id, 'English name'],
                          "Rating": anime_table.at[anime_id, 'Score'],
                          "Synopsis": anime_table.at[anime_id, 'Synopsis'],
                          "Genres": anime_table.at[anime_id, 'Genres'],
                          })
    response = json.loads(model.rate_multi_anime_by_request(json_list, request))['response']
    compliance_by_id = {}
    for anime in response:
        compliance_by_id[anime["anime_id"]] = anime['compliance_factor']
    final_list = []
    last_unsorted = [0 for i in anime_lists]
    for i in range(sum([len(i) for i in anime_lists])):
        l = [-1, -1, -1]
        for j in range(len(anime_lists)):
            if last_unsorted[j] != len(anime_lists[j]):
                l = max(l, [compliance_by_id[anime_lists[j][last_unsorted[j]]], j, anime_lists[j][last_unsorted[j]]])
        final_list.append(l[2])
        last_unsorted[l[1]] += 1
    return final_list

#print(merge_anime_based_on_request([[1393], [0], [7428]], "Хочу что-нибудь про монстров"))