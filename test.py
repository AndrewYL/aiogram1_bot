import asyncio
import sqlite3
import io
import logging
import threading
import time
import json
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import InputMediaDocument
from urllib.request import urlopen
API_TOKEN = '5282834057:AAGKZQR5A4HWvcE-oRr15Ucv_OPo2KCVdRA'

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


conn1 = sqlite3.connect("usersb.db")
cursor1 = conn1.cursor()


async def get_data():
    to = time.time()
    admin_id = 1234567899
    config_id = 12311
    # Пересылаем сообщение в данными от админа к админу
    forward_data = await bot.forward_message(admin_id, admin_id, config_id)

    # Получаем путь к файлу, который переслали
    file_data = await bot.get_file(forward_data.document.file_id)

    # Получаем файл по url
    file_url_data = bot.get_file_url(file_data.file_path)

    # Считываем данные с файла
    json_file= urlopen(file_url_data).read()
    print('Время получения бекапа :=' + str(time.time() - to))
    # Переводим данные из json в словарь и возвращаем
    return json.loads(json_file)


async def save_data():
    admin_id = 1234567899
    config_id = 12311
    to = time.time()
    sql = "SELECT * FROM users "
    cursor1.execute(sql)
    data = cursor1.fetchall()  # or use fetchone()
    try:
        # Переводим словарь в строку
        str_data=json.dumps(data)

        # Обновляем  наш файл с данными
        await bot.edit_message_media(InputMediaDocument(io.StringIO(str_data)), admin_id, config_id)

    except Exception as ex:
        print(ex)
    print('Время сохранения бекапа:='+str(time.time() - to))


class Form(StatesGroup):
    examen = State()
    predmet = State()
    answer = State()
    end_ans = State()
    wast_ans = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    sql_select = "SELECT * FROM users where chatid={}".format(message.from_user.id)
    sql_insert = "INSERT INTO users VALUES ({}, '{}', {},{})".format(message.from_user.id, message.from_user.first_name, 0, 0)
    try:
        cursor1.execute(sql_select)
        data = cursor1.fetchone()
        if data is None:
            cursor1.execute(sql_insert)
            conn1.commit()
            await save_data()
    except Exception:
        data = await get_data()
        cursor1.execute("CREATE TABLE users (chatid INTEGER , name TEXT, click INTEGER, state INTEGER)")
        cursor1.executemany("INSERT INTO users VALUES (?,?,?,?)", data)
        conn1.commit()
        cursor1.execute(sql_select)
        data = cursor1.fetchone()
        if data is None:
            cursor1.execute(sql_insert)
            conn1.commit()
            await save_data()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/oge")
    item2 = types.KeyboardButton("/ege")
    markup.add(item1)
    markup.add(item2)
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!👋 Выберите пожалуйста экзамен📝",
                         reply_markup=markup)


@dp.message_handler(state='*', commands=['help'])
@dp.message_handler(lambda message: message.text.lower() == 'help', state='*')
async def help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, 'Если вы застряли на выборе экзамена или предмета,\n'
                                                 'то выберите среди кнопок то, что вам нужно.\n'
                                                 'Если вы уже выбрали предмет и вам пришло задание,\n'
                                                 'то пришлите боту ответ на этот самый вопрос,\n'
                                                 'и не забывайте, у вас всегда есть 2 попытки на ответ!')


@dp.message_handler(state='*', commands=['rait'])
@dp.message_handler(lambda message: message.text.lower() == 'rait', state='*')
async def help_handler(message: types.Message):
    sql = "SELECT * FROM users ORDER BY click DESC LIMIT 15"
    cursor1.execute(sql)
    newlist = cursor1.fetchall()  # or use fetchone()
    sql_count = "SELECT COUNT(chatid) FROM users"
    cursor1.execute(sql_count)
    count = cursor1.fetchone()
    rating = 'Всего: {}\n'.format(count[0])
    i = 1
    for user in newlist:
        rating = rating + str(i) + ': ' + user[1] + ' - ' + str(user[2]) + '🏆\n'
        i += 1
    await bot.send_message(message.chat.id, rating)


@dp.message_handler(lambda message: message.text not in ["/oge",
                                                         "/ege"], state=Form.examen)
async def failed_process_examen(message: types.Message):

    return await message.reply("Вы неправильно ввели экзамен\n"
                               "Нажмите на одну из кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower() == '/oge')
async def process_oge(message: types.Message, state: FSMContext):
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
    markup.add(item1, item2)
    markup.add(item3, item4)
    markup.add(item5, item6)
    markup.add(item7, item8)
    markup.add(item9)
    await Form.predmet.set()
    await message.answer("Выберите предмет", reply_markup=markup)


@dp.message_handler(lambda message: message.text.lower() == '/ege')
async def process_ege(message: types.Message, state: FSMContext):
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
    markup.add(item1, item2)
    markup.add(item3, item4)
    markup.add(item5, item6)
    markup.add(item7, item8)
    markup.add(item9, item10)
    await Form.predmet.set()
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
                                                         'обществознание(егэ)', 'история(егэ)'], state=Form.predmet)
async def failed_process_predmet(message: types.Message):
    return await message.reply("Вы неправильно ввели предмет\n"
                               "Нажмите на одну из кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower(), state=Form.predmet)
async def process_predmet(message: types.Message, state: FSMContext):
    try:
        sql = "SELECT * FROM users where chatid={}".format(message.chat.id)
        cursor1.execute(sql)
        data1 = cursor1.fetchone()  # or use fetchone()
    except Exception:
        data1 = await get_data()
        cursor1.execute("CREATE TABLE users (chatid INTEGER , name TEXT, click INTEGER, state INTEGER)")
        cursor1.executemany("INSERT INTO users VALUES (?,?,?,?)", data1)
        conn1.commit()
        sql = "SELECT * FROM users where chatid={}".format(message.chat.id)
        cursor1.execute(sql)
        data1 = cursor1.fetchone()  # or use fetchone()
    async with state.proxy() as data:
        data['predmet'] = message.text
        await Form.answer.set()
        await state.update_data(predmet=message.text)
        if message.text.lower() == "русский язык(егэ)":
            if data is not None:
                sql = "UPDATE users SET click = {} WHERE chatid = {}".format(data1[2] + 1, message.chat.id)
                cursor1.execute(sql)
                conn1.commit()
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM rus_yaz
                WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.from_user.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "русский язык(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM rus_yaz
                WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'физика(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM fizika
                WHERE id IN (SELECT id FROM fizika ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'информатика(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM infor
                WHERE id IN (SELECT id FROM infor ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'химия(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM him
                WHERE id IN (SELECT id FROM him ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'биология(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM biol
                WHERE id IN (SELECT id FROM biol ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'география(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM geog
                WHERE id IN (SELECT id FROM geog ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'обществознание(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM obshes
                WHERE id IN (SELECT id FROM obshes ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == 'история(егэ)':
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM hist
                WHERE id IN (SELECT id FROM hist ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "профильная математика":
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM mat_prof
                WHERE id IN (SELECT id FROM mat_prof ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "базовая математика":
            con = sqlite3.connect('db/ege.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM mat_baz
                WHERE id IN (SELECT id FROM mat_baz ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "математика":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM matem
                 WHERE id IN (SELECT id FROM matem ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "физика(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM fizika
                 WHERE id IN (SELECT id FROM fizika ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "информатика(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM infor
                 WHERE id IN (SELECT id FROM infor ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "химия(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM him
                 WHERE id IN (SELECT id FROM him ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "биология(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM biol
                 WHERE id IN (SELECT id FROM biol ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "география(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM geog
                 WHERE id IN (SELECT id FROM geog ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "обществознание(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM obshes
                 WHERE id IN (SELECT id FROM obshes ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()
        if message.text.lower() == "история(огэ)":
            con = sqlite3.connect('db/oge.db')
            cur = con.cursor()
            result = cur.execute("""SELECT task, answer FROM hist
                 WHERE id IN (SELECT id FROM hist ORDER BY RANDOM() LIMIT 1)""").fetchall()
            for elem in result:
                print(f'{message.from_user.first_name}, {message.from_user.last_name}, {message.from_user.username}: '
                      f'{elem[1]}')
                data['answer'] = elem[1]
                await bot.send_photo(message.chat.id, photo=elem[0])
                await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            con.close()


@dp.message_handler(state=Form.answer)
async def last_answer(message: types.Message, state: FSMContext):
    answer = message.text
    otvet = await state.get_data()
    if ''.join(answer.lower().split()) == otvet['answer']:
        await bot.send_message(message.chat.id, 'Это правильный ответ!🎉')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Попробовать еще")
        item2 = types.KeyboardButton("Отказаться")
        markup.add(item1)
        markup.add(item2)
        await Form.end_ans.set()
        await bot.send_message(message.chat.id, 'Хотите попробовать еще?', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/start")
        markup.add(item)
        await state.reset_state(with_data=False)
        await bot.send_message(message.chat.id, 'Начнем с начала!', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/oge':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/oge")
        markup.add(item)
        await Form.examen.set()
        await bot.send_message(message.chat.id, 'Выберем другой предмет!', reply_markup=markup)
    elif ''.join(answer.lower().split()) == '/ege':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/ege")
        markup.add(item)
        await Form.examen.set()
        await bot.send_message(message.chat.id, 'Выберем другой предмет!', reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, 'К сожалению, это неправильный ответ. Однако у Вас есть возможность '
                                          'попробовать свои силы еще раз')
        await Form.wast_ans.set()


@dp.message_handler(state=Form.wast_ans)
async def last_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answer = message.text
        if ''.join(answer.lower().split()) == data['answer']:
            await bot.send_message(message.chat.id, 'Это правильный ответ!🎉')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Попробовать еще")
            item2 = types.KeyboardButton("Отказаться")
            markup.add(item1)
            markup.add(item2)
            await Form.end_ans.set()
            await bot.send_message(message.chat.id, 'Хотите попробовать еще?', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/start")
            markup.add(item)
            await state.reset_state(with_data=False)
            await bot.send_message(message.chat.id, 'Начнем с начала!', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/oge':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/oge")
            markup.add(item)
            await Form.examen.set()
            await bot.send_message(message.chat.id, 'Выберем другой предмет!', reply_markup=markup)
        elif ''.join(answer.lower().split()) == '/ege':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/ege")
            markup.add(item)
            await Form.examen.set()
            await bot.send_message(message.chat.id, 'Выберем другой предмет!', reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, md.text(
                md.text('К сожалению, это неправильный ответ'),
                md.text(md.code('Правильный ответ:'), md.bold(data['answer'])),
                sep='\n'), parse_mode=ParseMode.MARKDOWN)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Попробовать еще")
            item2 = types.KeyboardButton("Отказаться")
            markup.add(item1)
            markup.add(item2)
            await Form.end_ans.set()
            await bot.send_message(message.chat.id, 'Хотите попробовать еще?', reply_markup=markup)


@dp.message_handler(state=Form.end_ans)
async def process_end_ans(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        com = message.text
        if com.lower() == 'попробовать еще':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton(f"{data['predmet']}")
            markup.add(item)
            await Form.predmet.set()
            await bot.send_message(message.from_user.id, 'Начнем с начала', reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("/start")
            markup.add(item)
            await state.reset_state(with_data=False)
            await bot.send_message(message.from_user.id, 'До скорых встреч!', reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)