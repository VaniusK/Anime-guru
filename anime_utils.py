from imports import *

model = LLM()

anime_table = pd.read_csv("anime-dataset-2023.csv")
def gen_fich():
    return (item for item in (anime_table['Genres'] + ", " + anime_table['tags'] + ", " + anime_table['Type'] + ", " + anime_table['Studios'] + ", " + anime_table['Source']).values.astype('U'))

tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix_generator = tfidf.fit_transform(gen_fich())

cosine_sim_sparse = linear_kernel(tfidf_matrix_generator, tfidf_matrix_generator)

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
    for i in range(len(anime_lists)):
        anime_lists[i] = list(filter(lambda x: calculate_dropout_rate(user_id, x) <= random.random(), anime_lists[i]))
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
    print(response)
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

def get_similar_anime_by_content(idx: int) -> List[int]:
    sim_scores = list(enumerate(cosine_sim_sparse[idx]))

    valid_scores = [x for x in sim_scores if anime_table.iloc[x[0]]['Score'] != "UNKNOWN"]

    sorted_scores = sorted(valid_scores, key=lambda x: (x[1], anime_table.iloc[x[0]]['Score']), reverse=True)


    top_anime = [x for x in sorted_scores if x[0] != idx]

    recommended_anime = [idx for idx, _ in top_anime]
    return recommended_anime

def get_content_based_recommendations(user_preferences: Dict[int, int], amount_to_check: int, amount: int) -> List[int]:
    if len(user_preferences) == 0:
        return []
    viewed = list(user_preferences.keys())
    viewed.sort(key=lambda x: user_preferences[x])
    viewed.reverse()
    idxs = [random.randint(0, min(len(user_preferences) - 1, 5 * amount_to_check - 1)) for _ in range(amount_to_check)]
    similars = [get_similar_anime_by_content(viewed[i]) for i in idxs]
    ranks = Counter()
    for similar in similars:
        for i in range(len(similar)):
            ranks[similar[i]] -= 1 / (i + 1)
    ranked = list(ranks.keys())
    ranked = list(filter(lambda x: x not in viewed, ranked))
    ranked.sort(key=lambda x: ranks[x])

    return ranked[:amount]



'''
print(merge_anime_based_on_request([[1393], [0], [7428]], "Хочу что-нибудь про космос", 0))
exit()
animes = get_content_based_recommendations({947: 10, 0: 10}, 5, 10)
for anime in animes:
    print(anime_table.at[anime, "English name"], "\n", anime_table.at[anime, "Genres"], "\n", anime_table.at[anime, "tags"])
'''


