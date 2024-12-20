from imports import *

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]

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
# 11 - пролдолжать вводить аниме для добавления или нет
# 12 - пользователь выбирает, нравится ли ему первое предложенное аниме

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

df = pd.read_csv("anime-dataset-2023.csv")
name = df['English name']
sz = len(df["Name"])

# Находит набиолее похожую строку
async def find_closest_name(a):
    res = 0
    ds1 = 1000000
    j = 0
    b = a.lower()
    a = ""
    a1 = b.split()
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
        if cnt1 > res or (cnt1 == res and (ds < ds1 or (ds == ds1 and len(name[i]) < len(name[j])))):
            res = cnt1
            ds1 = ds
            j = i
    return j


async def choose_option(user_id):
    print(f'user{user_id} is choosing option')
    state_user[user_id] = 7
    tip = text(
            'Для того, чтобы нам было легче подобрать аниме под Вас, просим выбрать один из вариантов ниже'
        )
    await bot.send_message(user_id, tip, reply_markup=keyboard1)


@dp.message(Command(commands=['start']))
async def send_welcome(message):
    user_id = message.from_user.id
    print(f'{user_id} воспользовался командой /start') 
    if not user_id in state_user:
        state_user[user_id] = 1
        user_info[user_id] = dict() 
        user_rate_anime[user_id] = dict()
        user_watching[user_id] = dict()
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

@dp.message(Command(commands=['help']))
async def send_help(message):
    user_id = message.from_user.id
    print(f'{user_id} воспользовался командой /help')
    tip = text(
        '/suggest_anime - предложить аниме',
        '\n/add_anime - добавить аниме в список просмотренных',
        '\n/show_watched_anime - показать просмотренные аниме',
        '\n/start - старт', 
        '\n/help - о командах', 
        '\n/info - о проекте',
        '\n/reset - сбросить информацию о себе', 
        '\n/fill_form - заполнить форму'
    )
    await message.reply(tip)

@dp.message(Command(commands=['add_anime']))
async def add_anime(message):
    user_id = message.from_user.id
    if state_user[user_id] == 1:
        print(f'{user_id} добавляет аниме в свой лист')
        state_user[user_id] = 8
        await bot.send_message(user_id, "Для добавления аниме в список просмотренных, введите его название")
    else:
        await bot.delete_message(message.chat.id, message.message_id)

@dp.message(Command(commands=['show_watched_anime']))
async def show_watched_anime(message):
    user_id = message.from_user.id
    ls = ""
    ls += "Список просмотренных аниме:"
    for i in user_rate_anime[user_id]:
        ls += f'\n{name[i]} + (Ваша оценка: {user_rate_anime[user_id][i]})'
    await message.reply(ls)

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
            await bot.send_photo(user_id, photo=df["Image URL"][ls[0]], caption=f'Устраивает ли вас:{name[ls[0]]}?', reply_markup=keyboard3)

    else:
        await bot.delete_message(message.chat.id, message.message_id)



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
            await bot.send_message(user_id, "Просим вас написать пару названий аниме и оценку к ним\n", reply_markup=keyboard2)
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
        ind = await find_closest_name(text)
        print(df["anime_id"][ind], df["English name"][ind], df["Image URL"][ind])
        cur_anime[user_id] = ind
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы имели ввиду:{name[cur_anime[user_id]]}?', reply_markup=keyboard3)
        state_user[user_id] = 6
    elif state_user[user_id] == 5 or state_user[user_id] == 10:
        text = message.text
        if text.isdigit() and int(text) >= 1 and int(text) <= 10:
            user_rate_anime[user_id][cur_anime[user_id]] = int(text)
            await bot.send_message(user_id, f'Отлично! вы оценили {name[cur_anime[user_id]]} на {text}')
            if state_user[user_id] == 5:
                await bot.send_message(user_id, f'Просим дальше писать названия аниме и их оценку', reply_markup=keyboard2)
                state_user[user_id] = 4
            elif state_user[user_id] == 10:
                await bot.send_message(user_id, f'{name[cur_anime[user_id]]} успешно добавлено в Ваш список с оценкой {text}')
                state_user[user_id] = 1 
            cur_anime[user_id] = -1
        else:
            await bot.send_message(user_id, f'Пожалуйста оцените аниме {name[cur_anime[user_id]]} от 1 до 10')
    elif state_user[user_id] == 8:
        ind = await find_closest_name(message.text)
        state_user[user_id] = 9
        cur_anime[user_id] = ind
        await bot.send_photo(user_id, photo=df["Image URL"][ind], caption=f'Вы имели ввиду:{name[cur_anime[user_id]]}?', reply_markup=keyboard3)
    elif state_user[user_id] != 1:
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await bot.send_message(user_id, 'Просим вас использовать команды\n/help')


@dp.callback_query(lambda c: c.data == 'yes')
async def process_callback_fill_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
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
        await bot.send_message(user_id, "Отлично, теперь просим оценить данное аниме от 1 до 10")
        state_user[user_id] = 5
    elif state_user[user_id] == 9:
       await bot.send_message(user_id, "Отлично, теперь просим оценить данное аниме от 1 до 10")
       state_user[user_id] = 10
    elif state_user[user_id] == 11:
        await bot.send_message(user_id, "Тогда просим вводить названия аниме дальше")
        state_user[user_id] = 8
    elif state_user[user_id] == 12:
        await bot.send_message(user_id, "Рады, что смогли помочь")
        state_user[user_id] = 1
        cur_ls[user_id] = []


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
        await bot.send_message(user_id, "Значит мы не смогли понять вас(")
        await bot.send_message(user_id, "Продолжить ввод аниме?", reply_markup=keyboard3)
        state_user[user_id] = 11
        cur_anime[user_id] = -1
    elif state_user[user_id] == 11:
        await bot.send_message(user_id, "Вы перестали добавлять аниме")
        state_user[user_id] = 1
    elif state_user[user_id] == 12:
        ls = cur_ls[user_id]
        inline_list = [
                [InlineKeyboardButton(text=name[ls[1]], callback_data=str(ls[1]))], 
                [InlineKeyboardButton(text=name[ls[2]], callback_data=str(ls[2]))],
                [InlineKeyboardButton(text=name[ls[3]], callback_data=str(ls[3]))]
            ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_list)  
        await bot.send_message(user_id, "Может вас устроит что-нибудь из этого?", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == 'cancel')
async def process_callback_stop_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    print(f'{user_id} в состоянии {state_user[user_id]} воспользовался кнопкой отмена/прекратить')
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    if user_id in state_user and (state_user[user_id] == 2 or state_user[user_id] == 4):
        await bot.send_message(user_id, "Вы прекратили заполнение формы")
    state_user[user_id] = 1
    


if __name__ == '__main__':
    print("Started bot")
    dp.run_polling(bot)