from imports import *

anime_table = -1
users_refusals = {-1: {}}
users_watched_anime = {-1: {3533: 10, 947: 10}}


def load_data():
    global anime_table, users_refusals, users_watched_anime
    anime_table = pd.read_csv("anime-dataset-2023.csv", usecols=lambda x: "Unnamed" not in x)
    with open('users_refusals.pickle', 'rb') as file:
        users_refusals = pickle.load(file)
    with open('users_watched_anime.pickle', 'rb') as file:
        users_watched_anime = pickle.load(file)


def save_data():
    with open('users_refusals.pickle', 'wb') as file:
        pickle.dump(users_refusals, file)
    with open('users_watched_anime.pickle', 'wb') as file:
        pickle.dump(users_watched_anime, file)

load_data()
