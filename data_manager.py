from imports import *

anime_table = -1
users_refusals = -1

def load_data():
    global anime_table, users_refusals
    pd.read_csv("anime-dataset-2023.csv")
    with open('users_refusals.json', 'r') as file:
        users_refusals = json.load(file)


def save_data():
    with open('users_refusals.json', 'w') as file:
        json.dump(users_refusals, file)
