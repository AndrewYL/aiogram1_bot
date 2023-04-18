import asyncio
import sqlite3
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from tok_en import TOKEN

API_TOKEN = TOKEN  # импортируем токен бота из файла tok_en.py

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

storage = MemoryStorage()  # данные для пользователя, такие как правильный ответ и последний выбранный предмет
dp = Dispatcher(bot, storage=storage)  # будут храниться в оперативной памяти


class User(StatesGroup):  # здесь хранятся все состояния
    examen = State()
    predmet = State()
    answer = State()
    end_ans = State()
    wast_ans = State()


@dp.message_handler(commands=['start'])  # команда "/start"
async def start_handler(message: types.Message):
    await User.examen.set()  # включаем состояние выбора экзамена
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/oge")
    item2 = types.KeyboardButton("/ege")
    item3 = types.KeyboardButton('/stats')
    item4 = types.KeyboardButton('/help')
    markup.add(item1, item2)
    markup.add(item3, item4)  # добавляем кнопки
    db = sqlite3.connect('db/user_db.db')
    cdb = db.cursor()
    cdb.execute(f"SELECT user_id FROM users WHERE user_id = '{message.from_user.id}'")  # обращаемся к базе данных для
    if cdb.fetchone() is None:  # проверки, существует ли пользователь там
        cdb.execute(f"INSERT INTO users VALUES(?,?,?,?,?)",  # если нет, то добавляем его туда
                    (message.from_user.id, message.from_user.first_name, 0, 0, 0))
        db.commit()
    db.close()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!👋 Выберите пожалуйста экзамен📝",
                         reply_markup=markup)


# state = '*' позволяет этой команде вызываться в любой момент пользователем
@dp.message_handler(state='*', commands=['help'])  # команда "/help"
@dp.message_handler(lambda message: message.text.lower() == 'help', state='*')
async def help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, "Список команд:\n"
                                                 '/start - запуск бота\n'
                                                 '/oge - выбрать экзамен ОГЭ\n'
                                                 '/ege - выбрать экзамен ЕГЭ\n'
                                                 '/stats - показать статистику\n'
                                                 'Если вы не знаете, какой экзамен или предмет выбрать, '
                                                 'используйте кнопки на экране для выбора. Если вы уже выбрали предмет'
                                                 ' и получили задание, отправьте боту ответ на этот вопрос. '
                                                 'Если вы застряли в меню статистики и не можете вызвать другую команду,'
                                                 ' перезапустите бота, используя команду /start. И помните, что у '
                                                 'вас есть 2 попытки на ответ.')


@dp.message_handler(state='*', commands=['stats'])  # команда "/stats"
@dp.message_handler(lambda message: message.text.lower() == 'stats', state='*')
async def stats_handler(message: types.Message):
    db = sqlite3.connect('db/user_db.db')
    cdb = db.cursor()
    cdb.execute(f"SELECT user_id FROM users WHERE user_id = '{message.from_user.id}'")  # также проверяем наличие
    if cdb.fetchone() is None:  # пользователя в базе данных
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/start")
        markup.add(item1)
        cdb.execute(f"INSERT INTO users VALUES(?,?,?,?,?)",  # и также добавляем его туда при отсутствии
                    (message.from_user.id, message.from_user.first_name, 0, 0, 0))
        db.commit()
        db.close()
        await message.answer('Вы занесены в базу данных!Нажмите /stats ещё раз(так как вы сначала не нажали start)')
    else:
        result = cdb.execute(f"""SELECT all_ans, right_ans, wrong_ans FROM users
                            WHERE user_id = '{message.from_user.id}'""").fetchall()
        for elem in result:
            if elem[0] == 0:
                await bot.send_message(message.from_user.id, md.text(md.text(md.bold('Личная статистика📊:')),
                                                                     md.text(' '),
                                                                     md.text('Заданий выполнено: ', md.bold(elem[0])),
                                                                     md.text('Верных ответов: ', md.bold(elem[1]),
                                                                             ' (0%)'),
                                                                     md.text(f'Неверных ответов: ', md.bold(elem[2]),
                                                                             ' (0%)'),
                                                                     sep='\n'), parse_mode=ParseMode.MARKDOWN)
            else:
                await bot.send_message(message.from_user.id, md.text(md.text(md.bold('Личная статистика📊:')),
                                                                     md.text(' '),
                                                                     md.text('Заданий выполнено: ',
                                                                             md.bold(elem[0])),
                                                                     md.text('Верных ответов: ',
                                                                             md.bold(elem[1]),
                                                                     f' ({round((elem[1] / elem[0] * 100), 1)}%)'),
                                                                     md.text(f'Неверных ответов: ', md.bold(elem[2]),
                                                                     f' ({round((elem[2] / elem[0] * 100), 1)}%)'),
                                                                     sep='\n'), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda message: message.text not in ["/oge",  # хандлер для обработки ошибочного введения экзамена
                                                         "/ege"], state=User.examen)
async def failed_process_examen(message: types.Message):
    return await message.reply("Вы неправильно ввели экзамен\n"
                               "Нажмите на одну из кнопок для его выбора")


@dp.message_handler(lambda message: message.text.lower() == '/oge', state=User.examen)  # команда "/oge"
async def process_oge(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vibor_ex'] = 'oge'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Математика")
        item2 = types.KeyboardButton("Русский язык(ОГЭ)")
        item3 = types.KeyboardButton("Физика(ОГЭ)")
        item4 = types.KeyboardButton("Информатика(ОГЭ)")
        item5 = types.KeyboardButton("Химия(ОГЭ)")
        item6 = types.KeyboardButton("Биология(ОГЭ)")
        item7 = types.KeyboardButton("География(ОГЭ)")
        item8 = types.KeyboardButton("Обществознание(ОГЭ)")
        item9 = types.KeyboardButton("История(ОГЭ)")
        item10 = types.KeyboardButton('/stats')
        item11 = types.KeyboardButton('/help')
        markup.add(item1, item2)
        markup.add(item3, item4)
        markup.add(item5, item6)
        markup.add(item7, item8)
        markup.add(item9)
        markup.add(item10, item11)
        await User.predmet.set()  # включаем состояние выбора предмета
        await message.answer("Выберите предмет", reply_markup=markup)


@dp.message_handler(lambda message: message.text.lower() == '/ege', state=User.examen)  # команда "/ege"
async def process_ege(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vibor_ex'] = 'ege'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Профильная математика")
        item2 = types.KeyboardButton("Базовая математика")
        item3 = types.KeyboardButton("Русский язык(ЕГЭ)")
        item4 = types.KeyboardButton("Физика(ЕГЭ)")
        item5 = types.KeyboardButton("Информатика(ЕГЭ)")
        item6 = types.KeyboardButton("Химия(ЕГЭ)")
        item7 = types.KeyboardButton("Биология(ЕГЭ)")
        item8 = types.KeyboardButton("География(ЕГЭ)")
        item9 = types.KeyboardButton("Обществознание(ЕГЭ)")
        item10 = types.KeyboardButton("История(ЕГЭ)")
        item11 = types.KeyboardButton('/stats')
        item12 = types.KeyboardButton('/help')
        markup.add(item1, item2)
        markup.add(item3, item4)
        markup.add(item5, item6)
        markup.add(item7, item8)
        markup.add(item9, item10)
        markup.add(item11, item12)
        await User.predmet.set()  # включаем состояние выбора предмета
        await message.answer("Выберите предмет", reply_markup=markup)


@dp.message_handler(lambda message: message.text.lower() not in ['профильная математика',
                                                                 'базовая математика', 'русский язык(егэ)',
                                                                 'математика', 'русский язык(огэ)',
                                                                 'физика(огэ)', 'информатика(огэ)',
                                                                 'химия(огэ)', 'биология(огэ)',
                                                                 'география(огэ)', 'обществознание(огэ)',
                                                                 'история(огэ)', 'физика(егэ)',
                                                                 'информатика(егэ)', "химия(егэ)",
                                                                 'биология(егэ)', 'география(егэ)',
                                                                 'обществознание(егэ)', 'история(егэ)'],
                    state=User.predmet)  # хандлер для обработки ошибочного введения предмета
async def failed_process_predmet(message: types.Message):
    return await message.reply("Вы неправильно ввели предмет\n"
                               "Нажмите на одну из кнопок для его выбора")


@dp.message_handler(lambda message: message.text.lower(), state=User.predmet)
async def process_predmet(message: types.Message, state: FSMContext):
    conoge = sqlite3.connect('db/oge.db')
    conege = sqlite3.connect('db/ege.db')
    async with state.proxy() as data:
        data['predmet'] = message.text.lower()  # сохраняем выбранный пользователем предмет в оперативную память в виде словаря
        await User.answer.set()  # включаем состояние проверки первого ответа
        await state.update_data(predmet=message.text)
        slovar = {'русский язык(егэ)': 'rus_yaz', 'профильная математика': 'mat_prof', 'базовая математика': 'mat_baz',
                  'математика': 'matem', 'русский язык(огэ)': 'rus_yaz', 'физика(огэ)': 'fizika',
                  'информатика(огэ)': 'infor', 'химия(огэ)': 'him', 'биология(огэ)': 'biol', 'география(огэ)': 'geog',
                  'обществознание(огэ)': 'obshes', 'история(огэ)': 'hist', 'физика(егэ)': 'fizika', 'информатика(егэ)': 'infor',
                  "химия(егэ)": 'him', 'биология(егэ)': 'biol', 'география(егэ)': 'geog', 'обществознание(егэ)': 'obshes',
                  'история(егэ)': 'hist'}
        if data['vibor_ex'] == 'ege':
            cur = conege.cursor()
            result = cur.execute(f"""SELECT task, answer FROM {slovar[data['predmet']].lower()}
                            WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]  # сохраняем правильный ответ
                await bot.send_photo(message.from_user.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            conege.close()
        if data['vibor_ex'] == 'oge':
            cur = conoge.cursor()
            result = cur.execute(f"""SELECT task, answer FROM {slovar[data['predmet']].lower()}
                            WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]  # сохраняем правильный ответ
                await bot.send_photo(message.from_user.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            conege.close()


@dp.message_handler(state=User.answer)  # хандлер принимает введенный пользователем ответ
async def first_answer(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    if ''.join(answer.lower().split()) == data['answer']:  # сверяем ответ пользователя с правильным ответом
        db = sqlite3.connect('db/user_db.db')
        cdb = db.cursor()
        cdb.execute(f"UPDATE users SET all_ans = all_ans + 1 WHERE user_id = {message.from_user.id}")  # добавляем +1 к
        cdb.execute(f"UPDATE users SET right_ans = right_ans + 1 WHERE user_id = {message.from_user.id}")  # статистике
        db.commit()  # сделанных и правильно сделанных заданий
        db.close()
        await bot.send_message(message.from_user.id, 'Это правильный ответ!🎉')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Попробовать еще")
        item2 = types.KeyboardButton("Отказаться")
        item3 = types.KeyboardButton('/stats')
        item4 = types.KeyboardButton('/help')
        markup.add(item1, item2)
        markup.add(item3, item4)
        await User.end_ans.set()  # включаем состояние выбора продолжения выполнять задания или отказа от этого
        await bot.send_message(message.from_user.id, 'Хотите попробовать еще?', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/start")
        item1 = types.KeyboardButton('/stats')
        item2 = types.KeyboardButton('/help')
        markup.add(item, item1, item2)
        await state.reset_state(with_data=False)  # сбрасываем состояние
        await bot.send_message(message.from_user.id, 'Начнем с начала!', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/oge':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/oge")
        item1 = types.KeyboardButton('/stats')
        item2 = types.KeyboardButton('/help')
        markup.add(item, item1, item2)
        await User.examen.set()  # возвращаемся к состоянию выбора экзамена
        await bot.send_message(message.from_user.id, 'Выберем другой предмет!', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/ege':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/ege")
        item1 = types.KeyboardButton('/stats')
        item2 = types.KeyboardButton('/help')
        markup.add(item, item1, item2)
        await User.examen.set()  # возвращаемся к состоянию выбора экзамена
        await bot.send_message(message.from_user.id, 'Выберем другой предмет!', reply_markup=markup)
    else:
        await bot.send_message(message.from_user.id,
                               'К сожалению, это неправильный ответ. Однако у Вас есть возможность '
                               'попробовать свои силы еще раз')
        await User.wast_ans.set()  # включаем состояние проверки второго ответа пользователя


@dp.message_handler(state=User.wast_ans)
async def second_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answer = message.text
        db = sqlite3.connect('db/user_db.db')
        cdb = db.cursor()
        if ''.join(answer.lower().split()) == data['answer']:
            cdb.execute(f"UPDATE users SET all_ans = all_ans + 1 WHERE user_id = {message.from_user.id}")
            cdb.execute(f"UPDATE users SET right_ans = right_ans + 1 WHERE user_id = {message.from_user.id}")
            db.commit()
            db.close()
            await bot.send_message(message.from_user.id, 'Это правильный ответ!🎉')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Попробовать еще")
            item2 = types.KeyboardButton("Отказаться")
            item3 = types.KeyboardButton('/stats')
            item4 = types.KeyboardButton('/help')
            markup.add(item1, item2)
            markup.add(item3, item4)
            await User.end_ans.set()  # включаем состояние выбора продолжения выполнять задания или отказа от этого
            await bot.send_message(message.from_user.id, 'Хотите попробовать еще?', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/start")
            item1 = types.KeyboardButton('/stats')
            item2 = types.KeyboardButton('/help')
            markup.add(item, item1, item2)
            await state.reset_state(with_data=False)  # сбрасываем состояние
            await bot.send_message(message.from_user.id, 'Начнем с начала!', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/oge':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/oge")
            item1 = types.KeyboardButton('/stats')
            item2 = types.KeyboardButton('/help')
            markup.add(item, item1, item2)
            await User.examen.set()  # возвращаемся к состоянию выбора экзамена
            await bot.send_message(message.from_user.id, 'Выберем другой предмет!', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/ege':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/ege")
            item1 = types.KeyboardButton('/stats')
            item2 = types.KeyboardButton('/help')
            markup.add(item, item1, item2)
            await User.examen.set()  # возвращаемся к состоянию выбора экзамена
            await bot.send_message(message.from_user.id, 'Выберем другой предмет!', reply_markup=markup)
        else:
            cdb.execute(f"UPDATE users SET all_ans = all_ans + 1 WHERE user_id = {message.from_user.id}")
            cdb.execute(f"UPDATE users SET wrong_ans = wrong_ans + 1 WHERE user_id = {message.from_user.id}")
            db.commit()  # добавляем +1 в статистику пользователя к сделанным и неправильно сделанным заданиям
            db.close()
            await bot.send_message(message.from_user.id, md.text(
                md.text(md.bold('К сожалению, это неправильный ответ!')),
                md.text(md.code('Правильный ответ:'), md.bold(data['answer'])),
                sep='\n'), parse_mode=ParseMode.MARKDOWN)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Попробовать еще")
            item2 = types.KeyboardButton("Отказаться")
            item3 = types.KeyboardButton('/stats')
            item4 = types.KeyboardButton('/help')
            markup.add(item1, item2)
            markup.add(item3, item4)
            await User.end_ans.set()  # включаем состояние выбора продолжения выполнять задания или отказа от этого
            await bot.send_message(message.from_user.id, 'Хотите попробовать еще?', reply_markup=markup)


@dp.message_handler(state=User.end_ans)
async def process_end_ans(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        com = message.text
        if com.lower() == 'попробовать еще':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton(f"{data['predmet']}")  # добавляем пользователю кнопку для выбора последнего
            item1 = types.KeyboardButton('/stats')  # предмета
            item2 = types.KeyboardButton('/help')
            markup.add(item)
            markup.add(item1, item2)
            await User.predmet.set()  # возвращаемся к состоянию выбора предмета
            await bot.send_message(message.from_user.id, 'Начнем с начала', reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/start")
            item1 = types.KeyboardButton('/stats')
            item2 = types.KeyboardButton('/help')
            markup.add(item, item1, item2)
            await state.reset_state(with_data=False)  # сбрасываем состояние
            await bot.send_message(message.from_user.id, 'До скорых встреч!👋', reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
