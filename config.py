RECOMMENDATION_PROMPT = '''
Порекомендуй аниме, которое бы понравилось юзеру.
В своём ответе не выводи никакого текста, кроме, собственно, рекомендаций
Не используй форматирование, кроме переводов строк
Выведи список из 3-5 тайтлов. Для каждого должны быть указаны:
Название(В формате русское|английское|оригинальное(транслитом на английском, как kono suba). Если какого-то нет, пропускай)
Рейтинг(оценка от 1 до 10 из какой-то базы. Если нет данных - просто пропускай пункт, если есть, выводи в формате "Рейтинг: 7.1 по оценке того-то)
Описание(В формате "Описание: такое-то"). Содержание пункта не должно зависеть от запроса юзера
Теги(В формате "Теги: такие-то")
Почему именно аниме должно понравиться юзеру(ВАЖНО: Если это аниме никак не относится к запросу юзера, пропускай этот пункт). Выводи без заголовка
Ниже дан запрос юзера. Учти, что он может и не нести никакой полезной информации:

'''

GENERATE_TAGS_PROMPT = '''
Respond in ENGLISH
Create a string of tags for an anime based on its title and description.
If you know anything about this anime, you can use that knowledge.
The tags should most fully reveal the content of the anime.
Tags should not be tied specifically to this anime; other anime may have the same tags.
In particular, this means that you cannot use character names as tags.
Sort tags by relevance: With what probability will a user who likes this tag enjoy the anime?
Put the most relevant ones at the beginning.
Important note: You must NOT include genres(Aka "Comedy", "Fantasy" and stuff)
because we already have that data.
There must be 15-20 tags, no more than 25.
That means you can include more niche tropes as well
Request may contain several animes, give tags for each of them

'''

RATE_ANIME_PROMPT = '''
The above is a list of anime: ID, title, rating, synopsis and genres. 
For EACH anime, calculate the user preference matching factor: A fractional number from 0 to 1 with 3 decimal places of accuracy.
Important note: Even if anime doesn't fully correlate with user request, you should still give it some factor. 
For example, it may be similar genre to what user asks for.
Or, if anime has high rating, user may like it in general. 

'''