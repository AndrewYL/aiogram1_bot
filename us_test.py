import asyncio
import sqlite3
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

API_TOKEN = '5282834057:AAGKZQR5A4HWvcE-oRr15Ucv_OPo2KCVdRA'

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    examen = State()
    predmet = State()
    answer = State()
    end_ans = State()
    wast_ans = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await Form.examen.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/oge")
    item2 = types.KeyboardButton("/ege")
    markup.add(item1)
    markup.add(item2)
    db = sqlite3.connect('db/user_db.db')
    cdb = db.cursor()
    cdb.execute(f"SELECT user_id FROM users WHERE user_id = '{message.from_user.id}'")
    if cdb.fetchone() is None:
        cdb.execute(f"INSERT INTO users VALUES(?,?,?,?,?)",
                    (message.from_user.id, message.from_user.first_name, 0, 0, 0))
        db.commit()
    db.close()
    await message.answer(f"Здравствуйте, {message.from_user.first_name}!👋 Выберите пожалуйста экзамен📝",
                         reply_markup=markup)


@dp.message_handler(state='*', commands=['help'])
@dp.message_handler(lambda message: message.text.lower() == 'help', state='*')
async def help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, 'Если вы застряли на выборе экзамена или предмета, то выберите'
                                                 ' среди кнопок то, что вам нужно. '
                                                 'Если вы уже выбрали предмет и вам пришло задание, '
                                                 'то пришлите боту ответ на этот самый вопрос. '
                                                 'Если вы застряли в меню статистики и не можете вызвать другую'
                                                 ' любую команду, перезапустите бота командой /start. '
                                                 'И не забывайте, у вас всегда есть 2 попытки на ответ!')


@dp.message_handler(state='*', commands=['stats'])
@dp.message_handler(lambda message: message.text.lower() == 'stats', state='*')
async def stats_handler(message: types.Message):
    db = sqlite3.connect('db/user_db.db')
    cdb = db.cursor()
    cdb.execute(f"SELECT user_id FROM users WHERE user_id = '{message.from_user.id}'")
    if cdb.fetchone() is None:
        cdb.execute(f"INSERT INTO users VALUES(?,?,?,?,?)",
                    (message.from_user.id, message.from_user.first_name, 0, 0, 0))
        db.commit()
        db.close()
        await bot.send_message(message.from_user.id, 'Выполните хотя бы задание, чтобы появилась статистика!')
    else:
        result = cdb.execute(f"""SELECT all_ans, right_ans, wrong_ans FROM users
                        WHERE user_id = '{message.from_user.id}'""").fetchall()
        for elem in result:
            await bot.send_message(message.from_user.id, md.text(md.text(md.bold('Ваша статистика:')),
                                                                 md.text(' '),
                                                                 md.text('Заданий отправлено: ', md.bold(elem[0])),
                                                                 md.text(f'Верных ответов: ', md.bold(elem[1])),
                                                                 md.text(f'Неверных ответов: ', md.bold(elem[2])),
                                                                 sep='\n'), parse_mode=ParseMode.MARKDOWN)
        db.close()


@dp.message_handler(lambda message: message.text not in ["/oge",
                                                         "/ege"], state=Form.examen)
async def failed_process_examen(message: types.Message):
    return await message.reply("Вы неправильно ввели экзамен\n"
                               "Нажмите на одну из кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower() == '/oge', state=Form.examen)
async def process_oge(message: types.Message):
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


@dp.message_handler(lambda message: message.text.lower() == '/ege', state=Form.examen)
async def process_ege(message: types.Message):
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
                                                                 'обществознание(егэ)', 'история(егэ)'],
                    state=Form.predmet)
async def failed_process_predmet(message: types.Message):
    return await message.reply("Вы неправильно ввели предмет\n"
                               "Нажмите на одну из кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower(), state=Form.predmet)
async def process_predmet(message: types.Message, state: FSMContext):
    db = sqlite3.connect('db/user_db.db')
    cdb = db.cursor()
    cdb.execute(f"UPDATE users SET all_ans = all_ans + 1 WHERE user_id = {message.from_user.id}")
    db.commit()
    db.close()
    async with state.proxy() as data:
        data['predmet'] = message.text
        await Form.answer.set()
        await state.update_data(predmet=message.text)
        if message.text.lower() == "русский язык(егэ)":
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
        db = sqlite3.connect('db/user_db.db')
        cdb = db.cursor()
        cdb.execute(f"UPDATE users SET right_ans = right_ans + 1 WHERE user_id = {message.from_user.id}")
        db.commit()
        db.close()
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
            db = sqlite3.connect('db/user_db.db')
            cdb = db.cursor()
            cdb.execute(f"UPDATE users SET right_ans = right_ans + 1 WHERE user_id = {message.from_user.id}")
            db.commit()
            db.close()
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
            db = sqlite3.connect('db/user_db.db')
            cdb = db.cursor()
            cdb.execute(f"UPDATE users SET wrong_ans = wrong_ans + 1 WHERE user_id = {message.from_user.id}")
            db.commit()
            db.close()
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
