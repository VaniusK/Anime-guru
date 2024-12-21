from imports import *
users_refusals = data_manager.users_refusals
anime_table = data_manager.anime_table

model = LLM()



def calculate_dropout_rate(user_id, anime_id):
    if user_id not in users_refusals:
        return 0
    if anime_id not in users_refusals[user_id]:
        return 0
    time_passed = time.time() - users_refusals[user_id][anime_id][0]
    refusals_amount = users_refusals[user_id][anime_id][1]
    return 1 - (0.8 ** (refusals_amount / (1 + time_passed / (60 * 60 * 24))))

def merge_anime_based_on_request(anime_lists: List[List[int]], request: str, user_id: int) -> List[int]:
    merged_list = []
    random.shuffle(anime_lists)
    for i in range(len(anime_lists)):
        anime_lists[i] = list(filter(lambda x: calculate_dropout_rate(user_id, x) <= random.random(), anime_lists[i]))
    for anime_list in anime_lists:

        merged_list += anime_list
    return merged_list
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




'''
#print(merge_anime_based_on_request([[1393], [0], [7428]], "Хочу что-нибудь про космос", 0))
animes = get_content_based_recommendations({3533: 10, 947: 10}, 5, 20)
for anime in animes:
    print(anime_table.at[anime, "English name"], "\n", anime_table.at[anime, "Genres"], "\n", anime_table.at[anime, "tags"])
'''


