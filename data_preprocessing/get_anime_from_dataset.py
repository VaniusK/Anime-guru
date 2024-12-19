import gdown
import pandas as pd

# скачиваем датасеты
gdown.download(
    'https://drive.google.com/file/d/1JgDMDcHtvJ1UR-B-63jP89PHJOv4b_Wp/view?usp=drive_link',
    'rating.csv',
    quiet=False,
    fuzzy=True
)

gdown.download(
    'https://drive.google.com/file/d/1_IApnYkRAeZ2pjjWQXHQogwUeX7PPngu/view?usp=drive_link',
    'anime.csv',
    quiet=False,
    fuzzy=True
)

anime_table = pd.read_csv("./anime.csv").drop(columns='Unnamed: 0')
anime_table.to_csv("anime_table3.csv")