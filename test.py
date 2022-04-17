import asyncio
from typing import Optional
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

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    examen = State()  # Will be represented in storage as 'Form:name'
    predmet = State()  # Will be represented in storage as 'Form:age'
    answer = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.examen.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/oge")
    item2 = types.KeyboardButton("/ege")
    markup.add(item1)
    markup.add(item2)
    await message.answer("Привет! Выберите пожалуйста экзамен", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["/oge",
                                                         "/ege"], state=Form.examen)
async def failed_process_predmet(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Вы неправильно ввели экзамен\n"
                               "Нажмите на кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower() == '/oge', state=Form.examen)
async def process_examen(message: types.Message, state: FSMContext):
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
async def process_examen(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Профильная математика")
    item2 = types.KeyboardButton("Базовая математика")
    item3 = types.KeyboardButton("Русский язык(ЕГЭ)")
    item4 = types.KeyboardButton("Физика(ЕГЭ)")
    item5 = types.KeyboardButton("Информатика(ЕГЭ)")
    item6 = types.KeyboardButton("Химия(ЕГЭ)")
    item7 = types.KeyboardButton("Биология(ЕГЭ)")
    item8 = types.KeyboardButton("География(ЕГЭ)")
    markup.add(item1, item2)
    markup.add(item3, item4)
    markup.add(item5, item6)
    markup.add(item7, item8)
    await Form.predmet.set()
    await message.answer("Выберите предмет", reply_markup=markup)


# Check age. Age gotta be digit
@dp.message_handler(lambda message: message.text not in ["Профильная математика",
                                                         "Базовая математика", "Русский язык(ЕГЭ)",
                                                         'Математика', 'Русский язык(ОГЭ)',
                                                         'Физика(ОГЭ)', 'Информатика(ОГЭ)',
                                                         'Химия(ОГЭ)', 'Биология(ОГЭ)',
                                                         'География(ОГЭ)', 'Обществознание(ОГЭ)',
                                                         'История(ОГЭ)', 'Физика(ЕГЭ)',
                                                         "Информатика(ЕГЭ)", "Химия(ЕГЭ)",
                                                         "Биология(ЕГЭ)", "География(ЕГЭ)"], state=Form.predmet)
async def failed_process_predmet(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Вы неправильно ввели предмет\n"
                               "Нажмите на кнопку для его выбора")


@dp.message_handler(lambda message: message.text.lower(), state=Form.predmet)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.answer.set()
    await state.update_data(predmet=message.text)
    if message.text.lower() == "русский язык(егэ)":
        async with state.proxy() as data:
            data['predmet'] = message.text
        con = sqlite3.connect('db/ege.db')
        cur = con.cursor()
        result = cur.execute("""SELECT task, answer FROM rus_yaz
            WHERE id IN (SELECT id FROM rus_yaz ORDER BY RANDOM() LIMIT 1)""").fetchall()
        for elem in result:
            print(elem[1])
            correct = elem[1]
            async with state.proxy() as data:
                data['answer'] = correct
            await bot.send_photo(message.from_user.id, photo=elem[0])
            await bot.send_message(message.from_user.id, 'Ваш ответ:', reply_markup=types.ReplyKeyboardRemove())
        con.close()


@dp.message_handler(state=Form.answer)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id

        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(message.chat.id, md.text(
            md.text('Твой id', md.bold(data['user_id'])),
            md.text('Твой предмет:', data['predmet']),
            md.text('Твой правильный ответ:', data['answer']),
            sep='\n'), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

        # Finish conversation
        data.state = None


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)