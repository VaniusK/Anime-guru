from imports import *

anime_table=pd.read_csv('../anime-dataset-2023-with-common-tags-unfiltered.csv', usecols=lambda x: 'Unnamed' not in x)
anime_table = anime_table[~anime_table['Genres'].str.contains("Hentai")]
anime_table = anime_table.reset_index(drop=True)
anime_table.to_csv("../anime-dataset-2023-with-common-tags.csv")
