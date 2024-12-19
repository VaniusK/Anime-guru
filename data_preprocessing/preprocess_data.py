from imports import *

anime_table=pd.read_csv('../anime-dataset-2023-with-common-tags.csv', usecols=lambda x: 'Unnamed' not in x)
popularity_threshold = 50
anime_table= anime_table.query('Members >= @popularity_threshold')
anime_table= anime_table.reset_index(drop=True)
anime_table.to_csv("../anime-dataset-2023-with-common-tags.csv")
