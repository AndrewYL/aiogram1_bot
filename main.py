import asyncio
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
name = ''
correct = ''
bot = Bot(token='5282834057:AAGKZQR5A4HWvcE-oRr15Ucv_OPo2KCVdRA')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/oge")
    item2 = types.KeyboardButton("/ege")
    markup.add(item1)
    markup.add(item2)
    await bot.send_message(message.from_user.id, 'Выберите экзамен:', reply_markup=markup)


@dp.message_handler(commands=['oge'])
async def start_message(message):
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
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    markup.add(item5)
    markup.add(item6)
    markup.add(item7)
    markup.add(item8)
    markup.add(item9)
    await bot.send_message(message.from_user.id, 'Выберите предмет:', reply_markup=markup)


@dp.message_handler(commands=['ege'])
async def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Профильная математика")
    item2 = types.KeyboardButton("Базовая математика")
    item3 = types.KeyboardButton("Русский язык(ЕГЭ)")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    await bot.send_message(message.chat.id, 'Выберите предмет:', reply_markup=markup)


@dp.message_handler(content_types=['text'])
async def message_reply(message):
    global name
    global correct
    t = message.text
    if t.lower() == "русский язык(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Русский язык(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM rus_yaz
            WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(get_answer, content_types=message.text, state='*')
        con.close()
    if message.text.lower() == "русский язык(егэ)":
        con = sqlite3.connect('db/ege.db')
        cur = con.cursor()
        name = "Русский язык(ЕГЭ)"
        result = cur.execute("""SELECT task, answer FROM rus_yaz
            WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "профильная математика":
        con = sqlite3.connect('db/ege.db')
        cur = con.cursor()
        name = "Профильная математика"
        result = cur.execute("""SELECT task, answer FROM mat_prof
            WHERE id IN (SELECT id FROM mat_prof ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "базовая математика":
        con = sqlite3.connect('db/ege.db')
        cur = con.cursor()
        name = "Базовая математика"
        result = cur.execute("""SELECT task, answer FROM mat_baz
            WHERE id IN (SELECT id FROM mat_baz ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "математика":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Математика"
        result = cur.execute("""SELECT task, answer FROM matem
             WHERE id IN (SELECT id FROM matem ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "физика(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Физика(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM fizika
             WHERE id IN (SELECT id FROM fizika ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "информатика(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Информатика(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM infor
             WHERE id IN (SELECT id FROM infor ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "химия(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Химия(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM him
             WHERE id IN (SELECT id FROM him ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "биология(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Биология(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM biol
             WHERE id IN (SELECT id FROM biol ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "география(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "География(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM geog
             WHERE id IN (SELECT id FROM geog ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()
    if message.text.lower() == "обществознание(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "Обществознание(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM obshes
             WHERE id IN (SELECT id FROM obshes ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()

    if message.text.lower() == "история(огэ)":
        con = sqlite3.connect('db/oge.db')
        cur = con.cursor()
        name = "История(ОГЭ)"
        result = cur.execute("""SELECT task, answer FROM hist
             WHERE id IN (SELECT id FROM hist ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            await bot.send_photo(message.chat.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
            dp.register_message_handler(message, get_answer)
        con.close()


async def get_answer(message):
    global answer
    answer = message.text
    if ''.join(answer.lower().split()) == correct:

        await bot.send_message(message.chat.id, 'Правильный ответ!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Попробовать еще")
        item2 = types.KeyboardButton("Отказаться")
        markup.add(item1)
        markup.add(item2)
        await bot.send_message(message.chat.id, 'Хотите попробовать еще?', reply_markup=markup)
        await dp.register_message_handler(message, return0)


async def last_answer(message):
    global answer
    answer = message.text
    if ''.join(answer.lower().split()) == correct:
        await bot.send_message(message.chat.id, 'Правильный ответ!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Попробовать еще")
        item2 = types.KeyboardButton("Отказаться")
        markup.add(item1)
        markup.add(item2)
        await bot.send_message(message.chat.id, 'Хотите попробовать еще?', reply_markup=markup)
        await dp.register_message_handler(message, return0)


async def return0(message):
    com = message.text
    if com.lower() == 'попробовать еще':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton(f"{name}")
        markup.add(item)
        await bot.send_message(message.chat.id, 'Начнем с начала', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/start")
        markup.add(item)
        await bot.send_message(message.chat.id, 'До скорых встреч!', reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp)
