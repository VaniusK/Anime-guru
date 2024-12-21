from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import bold, code, italic, text
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram import F
from random import randint
import pandas as pd


import config


BOT_TOKEN = ""

# data_manager.load_data()
# df = data_manager.anime_table
df = pd.read_csv("dataset.csv")
name = df['English name']
sz = len(df["Name"])


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


user_rate_anime = dict() # Словарь, содержащий какую оценку пользователь поставил аниме(по ID)
user_watching = dict() # Словарь, содержащий какие аниме(по айди) сейчас смотрит пользователь
user_info = dict() # Словарь, содержащий информацию о пользователе(возраст, смотрел ли аниме или нет)
cur_anime = dict() # Словарь, какое аниме сейчас оценивает пользователь
state_user = dict() # Словарь, содержащий состояние пользователя
cur_ls = dict()
phrase= {
    "your_age": ""
}

# 1 - состояние ничего не происходит
# 2 - состояние заполнения формы(возраст)
# 3 - состояние заполнения формы(смотрели ли вы аниме)
# 4 - состояние заполнения формы(аниме)
# 5 - состояние заполнения формы(оценка аниме)
# 6 - ответ на вопрос да или нет(то ли аниме имелось ввиду)
# 7 - состояния ответа о выборе варианта
# 8 - состояние добавления аниме в свой лист
# 9 - ответ на вопрос то ли аниме добавить в лист
# 10 - состояние оценки аниме, добавленного в лист
# 11 - продолжать вводить аниме для добавления или нет
# 12 - пользователь выбирает, нравится ли ему первое предложенное аниме
# 13 - пользователь выбирает одно из других предложенных, либо же отмена
# 14 - добавление аниме в список смотрю сейчас
# 15 - то ли аниме имелось ввиду при добавлении в смотрю сейчас
# 16 - выбор варианта, относится к 8
# 17 - выбор варианта, относится к 15(14)
# 18 - добавлять рандомное аниме в список ?
# 19 - уверены ли вы, что хотите сбросить инфу о себе


# inline кнопки 
# Выбор 
inline_list1 = [
        [InlineKeyboardButton(text="Заполнить форму", callback_data="fill_form")],
        [InlineKeyboardButton(text="Написать о себе", callback_data="about_user")],
        [InlineKeyboardButton(text="Добавить свой список аниме", callback_data="add_list")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ]
keyboard1 = InlineKeyboardMarkup(inline_keyboard=inline_list1)

# Кнопки заполнения формы
inline_list2 = [
        [InlineKeyboardButton(text="Прекратить", callback_data="cancel")]
    ]
keyboard2 = InlineKeyboardMarkup(inline_keyboard=inline_list2)

# да или нет
inline_list3 = [
    [InlineKeyboardButton(text="Да", callback_data="yes")], 
    [InlineKeyboardButton(text="Нет", callback_data="no")]
]
keyboard3 = InlineKeyboardMarkup(inline_keyboard=inline_list3)

# Находит наиболее похожую строку
async def find_closest_name(a):
    res = 0
    ds1 = 1000000
    j = 0
    b = a.lower()
    a = ""
    a1 = b.split()
    ls = []
    for i in b:
        if (ord(i) >= ord('a') and ord(i) <= ord('z')) or i.isdigit():
            a += i
    for i in range(sz):
        s = name[i]
        s = s.lower()
        cnt = 0
        d = dict()
        for x in range(len(s)):
            if s[x] not in d:
                d[s[x]] = []
            d[s[x]].append(x)
        dp = [0]
        for x in range(len(a)):
            dp.append(10000)
        for x in range(len(a)):
            c = a[x]
            if c not in d:
                d[c] = []
            for y in range(len(d[c]) - 1, -1, -1):
                l = 0
                r = x + 1
                while r - l > 1:
                    m = (l + r) // 2
                    if d[c][y] > dp[m]:
                        l = m
                    else:
                        r = m
                dp[l + 1] = min(dp[l + 1], d[c][y])
        ds = 0
        for x in range(len(a) + 1):
            if dp[x] == 10000:
                break
            cnt = x
        if cnt * 100 > len(a) * 83:
            ds = len(b) - cnt
        else:
            ds = 40
        cnt1 = 0
        for x in a1:
            for y in s.split():
                if x in y:
                    cnt1 += len(x)
        ls.append([cnt1, -ds, -len(name[i]), i])
    ls = sorted(ls)
    ls = ls[::-1]
    return ls


async def choose_option(user_id):
    print(f'user{user_id} is choosing option')
    state_user[user_id] = 7
    tip = text(
            'Для того, чтобы нам было легче подобрать аниме под Вас, просим выбрать один из вариантов ниже'
        )
    await bot.send_message(user_id, tip, reply_markup=keyboard1)


@dp.message(Command(commands=['show_watching_anime']))
async def show_watching_anime(message):
    user_id = message.from_user.id
    ls = ""
    ls += "Список аниме, которые Вы сейчас смотрите:"
    j = 1
    for i in user_watching[user_id]:
        ls += f'\n{j}. {name[i]}'
        j += 1
    await message.reply(ls)


@dp.message(Command(commands=['show_watched_anime']))
async def show_watched_anime(message):
    user_id = message.from_user.id
    ls = ""
    ls += "Список просмотренных аниме:"
    j = 1
    for i in user_rate_anime[user_id]:
        ls += f'\n{j}. {name[i]}'
        if user_rate_anime[user_id][i] == 0:
            ls += "(Нет оценки)"
        else:
            ls += f'(Ваша оценка: {user_rate_anime[user_id][i]})'
        j += 1
    await message.reply(ls)


@dp.message(Command(commands=['add_anime']))
async def add_anime(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        print(f'{user_id} добавляет аниме в свой лист')
        state_user[user_id] = 8
        await bot.send_message(user_id, "Для добавления аниме в список просмотренных, введите его название")
    else:
        await bot.delete_message(message.chat.id, message.message_id)


@dp.message(Command(commands=['add_watching_anime']))
async def process_add_watching_anime(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        state_user[user_id] = 14
        await bot.send_message(user_id, "Для добавления аниме в список смотрю сейчас, введите его название")
    else:
        await bot.delete_message(message.chat.id, message.message_id)


@dp.message(Command(commands=['delete_watched_anime']))
async def process_delete_watched_anime(message):
    user_id = message.from_user.id
    text = message.text
    if text.find('#') == -1 or not (text[text.find('#') + 1:].strip().isdigit()):
        await message.reply("Вводите команду в формате:\n/delete_watched_anime #(порядковый номер аниме в списке просмотренных)")
    else:
        ind = int(text[text.find('#') + 1:].strip())
        ls = dict()
        j = 1
        for i in user_rate_anime[user_id]:
            if j == ind:
                await message.reply(f"{name[i]} успешно удалено из списка просмотренных")
            else:
                ls[i] = user_rate_anime[user_id][i]
            j += 1
        user_rate_anime[user_id] = ls


@dp.message(Command(commands=['delete_watching_anime']))
async def process_delete_watching_anime(message):
    user_id = message.from_user.id
    text = message.text
    if text.find('#') == -1 or not (text[text.find('#') + 1:].strip().isdigit()):
        await message.reply("Вводите команду в формате:\n/delete_watching_anime #(порядковый номер аниме в списке смотрю сейчас)")
    else:
        ind = int(text[text.find('#') + 1:].strip())
        ls = []
        j = 1
        for i in user_watching[user_id]:
            if j == ind:
                await message.reply(f"{name[i]} успешно удалено из списка смотрю сейчас")
            else:
                ls.append(i)
            j += 1
        user_watching[user_id] = ls


@dp.message(Command(commands=['random']))
async def process_random(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        ind = randint(0, sz)
        genres = df['Genres'][ind]
        cur_anime[user_id] = ind
        tip = text(f'Рандомное аниме:{name[ind]}',
                f'\n\nЖанры:{df["Genres"][ind]}', 
                f'\n\nВозрастной рейтинг: {df["Rating"][ind]}',
                f'\n\nРейтинг: {df["Score"][ind]}', 
                f'\n\nПродюссер: {df["Producers"][ind]}',
                f'\n\nОписание: {df["Synopsis"][ind][0:min(145, len(df["Synopsis"][ind]))]}...', 
                f'\n\nДобавить в список смотрю сейчас?'
        )
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=tip, reply_markup=keyboard3)
        state_user[user_id] = 18
    else:
        await bot.delete_message(message.chat.id, message.message_id)


@dp.message(Command(commands=['start']))
async def send_welcome(message):
    user_id = message.from_user.id
    print(f'{user_id} воспользовался командой /start') 
    if not user_id in state_user:
        state_user[user_id] = 1
        user_info[user_id] = dict() 
        user_rate_anime[user_id] = dict()
        user_watching[user_id] = list()
        cur_anime[user_id] = -1
        cur_ls[user_id] = []
    tip = text(
        'Привет!', 
        '\nАниме-гуру бот поможет Вам с подбором аниме в зависимости от ваших предпочтений',
        '\nДля того, чтобы бот посоветовал аниме, используйте команду', 
        '\n/suggest_anime', 
        '\nПомощь по командам',
        '\n/help'  
        )
    await message.reply(tip)

@dp.message(Command(commands=['stop']))
async def stop(message):
    user_id = message.from_user.id
    state_user[user_id] = 1


@dp.message(Command(commands=['help']))
async def send_help(message):
    user_id = message.from_user.id
    print(f'{user_id} воспользовался командой /help')
    tip = text(
        '/suggest_anime - предложить аниме',
        '\n/random - выдать рандомное аниме', 
        '\n/add_anime - добавить аниме в список просмотренных',
        '\n/add_watching_anime - добавить аниме в список смотрю сейчас',
        '\n/show_watched_anime - показать просмотренные аниме',
        '\n/show_watching_anime - показать список аниме, которые смотрю сейчас',
        '\n/delete_watching_anime - удалить аниме из списка смотрю сейчас',
        '\n/delete_watched_anime - удалить аниме из списка просмотренных',
        '\n/start - старт', 
        '\n/help - о командах', 
        '\n/info - о проекте',
        '\n/reset - сбросить информацию о себе', 
        '\n/fill_form - заполнить форму', 
        '\n/stop - прекратить(если что-то пошло не так)'
    )
    await message.reply(tip)


@dp.message(Command(commands=['info']))
async def send_info(message):
    user_id = message.from_user.id
    print(f'{user_id} воспользовался командой /info')
    info = text(
    'В рамках проекта разработан telegram-бот, в общении',
    '\nс которым можно получить рекомендации для',
    '\nвыбора аниме согласно своим предпочтениям.',
    '\nРеализация включает в себя разработку непосредственно',
    '\ntelegram-бота с помощью API; изучение и анализ данных;',
    '\nвыбор и реализация алгоритма рекомендаций.',
    '\nВ ходе работы предстояло справиться с инфраструктурными' ,
    '\nвызовами и трудностями построения рекомендательных систем:', 
    '\nхолодным стартом, глобальной популярностью, устареванием контента и др.'
    )
    await message.reply(info)

@dp.message(Command(commands=['suggest_anime']))
async def send_anime(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        if len(user_rate_anime[user_id]) < 1:
            await bot.send_message(user_id, "У нас мало информации о Вас, поэтому просим\nзаполнить форму, либо же добавить аниме\n/fill_form\n/add_anime")
        else:
            ls = []
            for i in range(4):
                ls.append(randint(0, 5000))
            state_user[user_id] = 12
            cur_ls[user_id] = ls
            ind = ls[0]
            tip = text(
                f'Устраивает ли вас:{name[ind]}?'
                f'\n\nЖанры:{df["Genres"][ind]}', 
                f'\n\nВозрастной рейтинг: {df["Rating"][ind]}',
                f'\n\nРейтинг: {df["Score"][ind]}', 
                f'\n\nПродюссер: {df["Producers"][ind]}',
                f'\n\nОписание: {df["Synopsis"][ind][0:min(145, len(df["Synopsis"][ind]))]}...'
            )
            await bot.send_photo(user_id, photo=df["Image URL"][ls[0]], caption=tip, reply_markup=keyboard3)
    else:
        await bot.delete_message(message.chat.id, message.message_id)

@dp.message(Command(commands=['reset']))
async def process_callback_fill_button(message):
    user_id = message.from_user.id
    state_user[user_id] = 19
    await message.reply("Вы уверены, что хотите сбросить информацию о себе?\nВсе ваши списки очистятся", reply_markup=keyboard3)
    


@dp.message(Command(commands=['fill_form']))
async def process_callback_fill_button(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        print(f'{user_id} выбрал заполнить форму')
        tip = text(
            'Вы выбрали заполнение формы',
            '\nПросим Вас ответить на наши вопросы'
        )
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(user_id, tip)
        if 'age' not in user_info[user_id]:
            state_user[user_id] = 2
            await bot.send_message(user_id, "Какой Ваш возраст(полных лет)?")
        elif 'watched_anime' not in user_info[user_id]:
            state_user[user_id] = 3
            await bot.send_message(user_id, "Смотрели ли вы аниме?", reply_markup=keyboard3)
        else:
            state_user[user_id] = 4
            await bot.send_message(user_id, "Просим вас написать пару названий аниме и оценку к ним\nВводите названия по одному", reply_markup=keyboard2)
    else:
        await bot.delete_message(message.chat.id, message.message_id)



@dp.message(F.text)
async def process_states(message):
    user_id = message.from_user.id
    print(user_rate_anime[user_id])
    if state_user[user_id] == 2:
        print(f'{user_id} в состоянии {state_user[user_id]} написал {message.text}')
        text = message.text
        if text.isdigit():
            await message.reply("Спасибо за ответ")
            state_user[user_id] = 3
            user_info[user_id]['age'] = int(text)
            await bot.send_message(user_id, "Смотрели ли вы аниме?", reply_markup=keyboard3)
        else: 
            await message.reply("Введите ваш возраст в виде целого положительного числа")
    elif state_user[user_id] == 4:
        text = message.text
        ls = await find_closest_name(text)
        ind = ls[0][3]
        print(df["anime_id"][ind], df["English name"][ind], df["Image URL"][ind])
        cur_anime[user_id] = ind
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы имели ввиду:{name[cur_anime[user_id]]}?', reply_markup=keyboard3)
        state_user[user_id] = 6
    elif state_user[user_id] == 5 or state_user[user_id] == 10:
        text = message.text
        if text.isdigit() and int(text) >= 0 and int(text) <= 10:
            user_rate_anime[user_id][cur_anime[user_id]] = int(text)
            if int(text) != 0:
                await bot.send_message(user_id, f'Отлично! вы оценили {name[cur_anime[user_id]]} на {text}')
            if state_user[user_id] == 5:
                await bot.send_message(user_id, f'Просим дальше писать названия аниме и их оценку', reply_markup=keyboard2)
                state_user[user_id] = 4
            elif state_user[user_id] == 10:
                if int(text) != 0:
                    await bot.send_message(user_id, f'{name[cur_anime[user_id]]} успешно добавлено в список просмотренных с оценкой {text}')
                else:
                    await bot.send_message(user_id, f'{name[cur_anime[user_id]]} успешно добавлено в список просмотренных')
                state_user[user_id] = 1 
            cur_anime[user_id] = -1
        else:
            await bot.send_message(user_id, f'Пожалуйста оцените аниме {name[cur_anime[user_id]]} от 1 до 10\nВведите 0 если не хотите оценивать сейчас')
    elif state_user[user_id] == 8:
        ls = await find_closest_name(message.text)
        ind = ls[0][3]
        state_user[user_id] = 9
        cur_anime[user_id] = ind
        cur_ls[user_id] = ls[0:5]
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы имели ввиду:{name[cur_anime[user_id]]}?', reply_markup=keyboard3)
    elif state_user[user_id] == 14:
        ls = await find_closest_name(message.text)
        ind = ls[0][3]
        state_user[user_id] = 15
        cur_anime[user_id] = ind
        cur_ls[user_id] = ls[0:5]
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы имели ввиду:{name[cur_anime[user_id]]}?', reply_markup=keyboard3)
    elif state_user[user_id] != 1:
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await bot.send_message(user_id, 'Просим вас использовать команды\n/help')

@dp.callback_query(lambda c: c.data.startswith('choice'))
async def process_callback_choice(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print("here we came")
    print(callback_query.data)
    if state_user[user_id] == 13:
        ind = int(callback_query.data[callback_query.data.find(":") + 1:])
        tip = text(f'Вы выбрали:{name[ind]}\nОтличный выбор! Добавим в список смотрю сейчас',
                f'\n\nЖанры:{df["Genres"][ind]}', 
                f'\n\nВозрастной рейтинг: {df["Rating"][ind]}',
                f'\n\nРейтинг: {df["Score"][ind]}', 
                f'\n\nПродюссер: {df["Producers"][ind]}',
                f'\n\nОписание: {df["Synopsis"][ind][0:min(145, len(df["Synopsis"][ind]))]}...'
        )
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=tip)
        user_watching[user_id].append(ind)
        state_user[user_id] = 1
    elif state_user[user_id] == 16:
        ind = int(callback_query.data[callback_query.data.find(":") + 1:])
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы выбрали:{name[ind]}\nПросим оценить от 1 до 10\nВведите 0 если не хотите оценивать сейчас')
        cur_anime[user_id] = ind
        state_user[user_id] = 10
    elif state_user[user_id] == 17:
        ind = int(callback_query.data[callback_query.data.find(":") + 1:])
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы добавили:{name[ind]} в список смотрю сейчас')
        cur_anime[user_id] = ind
        user_watching[user_id].append(ind)
        state_user[user_id] = 1

        


@dp.callback_query(lambda c: c.data == 'yes')
async def process_callback_fill_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print(user_id)
    if state_user[user_id] == 3:
        tip = text(
            "Отлично!", 
            "\nВ таком случае попросим Вас название одного из аниме, которые Вы смотрели",
            "\nЧем больше мы узнаем, тем легче нам будет подобрать аниме под Вас"
        )
        user_info[user_id]['watched_anime'] = True
        print(user_info)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(user_id, tip, reply_markup=keyboard2)
        state_user[user_id] = 4
    elif state_user[user_id] == 6:
        await bot.send_message(user_id, "Отлично, теперь просим оценить данное аниме от 1 до 10\nВведите 0 если не хотите оценивать сейчас")
        state_user[user_id] = 5
    elif state_user[user_id] == 9:
       await bot.send_message(user_id, "Отлично, теперь просим оценить данное аниме от 1 до 10\nВведите 0 если не хотите оценивать сейчас")
       state_user[user_id] = 10
    elif state_user[user_id] == 11:
        await bot.send_message(user_id, "Тогда просим вводить названия аниме дальше")
        state_user[user_id] = 8
    elif state_user[user_id] == 12:
        ind = cur_ls[user_id][0]
        await bot.send_message(user_id, f"Рады, что смогли помочь.\n{name[ind]} добавлено в список смотрю сейчас")
        user_watching[user_id].append(ind)
        state_user[user_id] = 1
    elif state_user[user_id] == 15:
        ind = cur_ls[user_id][0][3]
        await bot.send_message(user_id, f"Рады, что смогли помочь.\n{name[ind]} добавлено в список смотрю сейчас")
        user_watching[user_id].append(ind)
        state_user[user_id] = 1
    elif state_user[user_id] == 18:
        ind = cur_anime[user_id]
        await bot.send_message(user_id, f"{name[ind]} добавлено в список смотрю сейчас")
        user_watching[user_id].append(ind)
        state_user[user_id] = 1
    elif state_user[user_id] == 19:
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(user_id, "Вы сбросили информацию о себе:(")
        state_user[user_id] = 1
        user_info[user_id] = dict() 
        user_rate_anime[user_id] = dict()
        user_watching[user_id] = list()
        cur_anime[user_id] = -1
        cur_ls[user_id] = []
    else:
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.callback_query(lambda c: c.data == 'no')
async def process_callback_fill_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if state_user[user_id] == 3:
        tip = text(
            "Очень жаль:(", 
            "\nВ таком случае подбор аниме будет сложнее"
        )
        user_info[user_id]['watched_anime'] = False
        print(user_info)
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message(user_id, tip)
        state_user[user_id] = 1
    elif state_user[user_id] == 6:
        await bot.send_message(user_id, "Значит мы не смогли понять вас(")
        await bot.send_message(user_id, "Просим дальше писать названия аниме и их оценку", reply_markup=keyboard2)
        state_user[user_id] = 4
        cur_anime[user_id] = -1
    elif state_user[user_id] == 9:
        ls = cur_ls[user_id]
        inline_list = []
        for i in range(1, 4):
            inline_list.append([InlineKeyboardButton(text=name[ls[i][3]], callback_data=f'choice:{ls[i][3]}')])
        inline_list.append([InlineKeyboardButton(text="Нет ничего подходящего", callback_data="cancel")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_list)
        state_user[user_id] = 16  
        await bot.send_message(user_id, "Может быть вы имели ввиду что-нибудь из этого?", reply_markup=keyboard)
    elif state_user[user_id] == 11:
        await bot.send_message(user_id, "Вы перестали добавлять аниме")
        state_user[user_id] = 1
    elif state_user[user_id] == 12:
        ls = cur_ls[user_id]
        inline_list = []
        print(ls)
        for i in range(1, 4):
            inline_list.append([InlineKeyboardButton(text=name[ls[i]], callback_data=f'choice:{ls[i]}')])
        inline_list.append([InlineKeyboardButton(text="Нет ничего подходящего", callback_data="cancel")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_list)  
        await bot.send_message(user_id, "Может вас устроит что-нибудь из этого?", reply_markup=keyboard)
        state_user[user_id] = 13
    elif state_user[user_id] == 15:
        ls = cur_ls[user_id]
        inline_list = []
        for i in range(1, 4):
            inline_list.append([InlineKeyboardButton(text=name[ls[i][3]], callback_data=f'choice:{ls[i][3]}')])
        inline_list.append([InlineKeyboardButton(text="Нет ничего подходящего", callback_data="cancel")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_list)  
        await bot.send_message(user_id, "Может вас устроит что-нибудь из этого?", reply_markup=keyboard)
        state_user[user_id] = 17
    elif state_user[user_id] == 18:
        await bot.send_message(user_id, "Вы решили не добавлять рандомное аниме")
        state_user[user_id] = 1
    elif state_user[user_id] == 19:
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        state_user[user_id] = 1
    else:
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.callback_query(lambda c: c.data == 'cancel')
async def process_callback_stop_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print(f'{user_id} в состоянии {state_user[user_id]} воспользовался кнопкой отмена/прекратить')
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    if user_id in state_user and (state_user[user_id] == 2 or state_user[user_id] == 4):
        await bot.send_message(user_id, "Вы прекратили заполнение формы")
        state_user[user_id] = 1
    elif state_user[user_id] == 13:
        await bot.send_message(user_id, "Очень жаль, что мы не смогли вам помочь(")
        state_user[user_id] = 1
    elif state_user[user_id] == 16:
        await bot.send_message(user_id, "Значит мы не смогли понять вас")
        await bot.send_message(user_id, "Продолжить ввод аниме?", reply_markup=keyboard3)
        state_user[user_id] = 11
    elif state_user[user_id] == 17:
        await bot.send_message(user_id, "Значит мы не смогли понять вас")
        state_user[user_id] = 1
    


if __name__ == '__main__':
    print("Started bot")
    dp.run_polling(bot)