from imports import *
from recommendation_systems.content_based_recommendations import get_content_based_recommendations
import anime_utils
users_watched_anime = data_manager.users_watched_anime



def get_recommendations(user_id: int, request: str) -> List[int]:
    if not user_id in users_watched_anime:
        users_watched_anime[user_id] = {}
    user_preferences = users_watched_anime[user_id]
    anime_lists = [
        get_content_based_recommendations(user_preferences, 5, 10)
    ]
    return anime_utils.merge_anime_based_on_request(anime_lists, request, user_id)[:100]

'''
animes = get_recommendations(-1, "")[:10]
for anime in animes:
    print(data_manager.anime_table.loc[anime]['English name'])
'''
