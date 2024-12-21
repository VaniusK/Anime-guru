from imports import *

anime_table = data_manager.anime_table
def gen_fich():
    return (item for item in (anime_table['Genres'] + " | " + anime_table['tags'] + " | " + anime_table['Type'] + " | " + anime_table['Studios'] + " | " + anime_table['Source']).values.astype('U'))

tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix_generator = tfidf.fit_transform(gen_fich())

cosine_sim_sparse = linear_kernel(tfidf_matrix_generator, tfidf_matrix_generator)

def get_similar_anime_by_content(idx: int) -> List[int]:
    sim_scores = list(enumerate(cosine_sim_sparse[idx]))

    valid_scores = [x for x in sim_scores if anime_table.iloc[x[0]]['Score'] != "UNKNOWN"]

    sorted_scores = sorted(valid_scores, key=lambda x: (x[1], anime_table.iloc[x[0]]['Score']), reverse=True)


    top_anime = [x for x in sorted_scores if x[0] != idx]

    recommended_anime = [idx for idx, _ in top_anime]
    return recommended_anime

def get_content_based_recommendations(user_preferences: Dict[int, int], amount_to_check: int , amount: int) -> List[int]:
    if len(user_preferences) == 0:
        return []
    viewed = list(user_preferences.keys())
    viewed.sort(key=lambda x: user_preferences[x])
    viewed.reverse()
    idxs = [random.randint(0, min(len(user_preferences) - 1, 5 * amount_to_check - 1)) for _ in range(amount_to_check)]
    similars = [get_similar_anime_by_content(viewed[i]) for i in idxs]
    ranks = Counter()
    for j in range(len(similars)):
        similar = similars[j]
        for i in range(len(similar)):
            ranks[similar[i]] -= 1 / (i + 1) * (user_preferences[viewed[idxs[j]]] or 1)
    ranked = list(ranks.keys())
    ranked = list(filter(lambda x: x not in viewed, ranked))
    ranked.sort(key=lambda x: ranks[x])

    return ranked[:amount]
