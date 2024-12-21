from imports import *

anime_table = -1
users_refusals = {-1: {}}
users_watched_anime = {-1: {3533: 10, 947: 10}}
users_watching = {}
users_info = {}
cur_anime = {}
state_user = {}
cur_ls = {}


def load_data():
    global anime_table, users_refusals, users_watched_anime, users_watching, users_info, cur_anime, state_user, cur_ls
    anime_table = pd.read_csv("anime-dataset-2023.csv", usecols=lambda x: "Unnamed" not in x)
    with open('users_refusals.pickle', 'rb') as file:
        users_refusals = pickle.load(file)
    with open('users_watched_anime.pickle', 'rb') as file:
        users_watched_anime = pickle.load(file)
    with open('users_watching.pickle', 'rb') as file:
        users_watching = pickle.load(file)
    with open('users_info.pickle', 'rb') as file:
        users_info = pickle.load(file)
    with open('cur_anime.pickle', 'rb') as file:
        cur_anime = pickle.load(file)
    with open('state_user.pickle', 'rb') as file:
        state_user = pickle.load(file)
    with open('cur_ls.pickle', 'rb') as file:
        cur_ls = pickle.load(file)
    print("Data loaded")


def save_data():
    with open('users_refusals.pickle', 'wb') as file:
        pickle.dump(users_refusals, file)
    with open('users_watched_anime.pickle', 'wb') as file:
        pickle.dump(users_watched_anime, file)
    with open('users_watching.pickle', 'wb') as file:
        pickle.dump(users_watching, file)
    with open('users_info.pickle', 'wb') as file:
        pickle.dump(users_info, file)
    with open('cur_anime.pickle', 'wb') as file:
        pickle.dump(cur_anime, file)
    with open('state_user.pickle', 'wb') as file:
        pickle.dump(state_user, file)
    with open('cur_ls.pickle', 'wb') as file:
        pickle.dump(cur_ls, file)
    print("Data saved")


load_data()
