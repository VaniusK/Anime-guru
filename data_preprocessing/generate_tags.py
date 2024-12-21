from imports import *
model = LLM()

all_tags = Counter()
available_tags = set()

def clean_tags(tags):
    tags = [x.lower() for x in tags]
    tags = list(map(lambda x: x.replace("-", ""), tags))
    for i in range(len(tags)):
        if tags[i][0] == ' ':
            tags[i] = tags[i][1:]
        if tags[i][-1] == ' ':
            tags[i] = tags[i][:-1]
    return tags


anime_table = pd.read_csv("anime-dataset-2023-2.csv")
k = 10
anime_list = []
print("started")

'''

for i in range(0, len(anime_table)):
    anime_table.at[i, "tags"] = eval(anime_table.at[i, "tags"])
    if anime_table.at[i, "Synopsis"] == "UNKNOWN":
        anime_table.at[i, "tags"] = []
anime_table.to_csv("anime-dataset-2023-2.csv")



for i in range(0, len(anime_table)):
    anime_list.append([i, anime_table.at[i, "English name"], anime_table.at[i, "Synopsis"]])
    if len(anime_list) == k or i == len(anime_table) - 1:
        response = json.loads(model.generate_multi_tags(anime_list))['response']
        for anime in response:
            anime_table.at[anime['anime_id'], "tags"] = clean_tags(anime['tags'])
            print(clean_tags(anime['tags']))
        anime_list = []
        print(i)
'''


for i in range(0, len(anime_table)):

    for tag in eval(anime_table.at[i,'tags']):
        tag = tag.replace("\"", "")
        tag = tag.replace("\'", "")
        all_tags[tag] += 1
l = [[all_tags[i], i] for i in all_tags]
l.sort()
l.reverse()
l = l[:150]
print(l)

for i in range(0, len(anime_table)):
    new_tags = []
    for tag in eval(anime_table.at[i,'tags']):
        tag = tag.replace("\"", "")
        tag = tag.replace("\'", "")
        if [all_tags[tag], tag] in l:
            new_tags.append(tag)
    anime_table.at[i, 'tags'] = new_tags
anime_table.to_csv("anime-dataset-2023-3.csv")