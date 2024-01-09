import asyncio
import logging
import os
import pymysql
import mysql.connector
from aiohttp import request
from typing import Any, Dict
from aiogram import Bot, Dispatcher, html, types, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from mysql.connector import Error

from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import TOKEN
from utils import Form

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher()

    
# Подключение к базе данных MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    db='Estate_db',
)

my_router = Router(name= __name__)

# Обработка команды /start, также здесь создается таблица в базе данных
@my_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.username)
    await message.answer(
        "Привет! Как Вас зовут?",
        reply_markup=ReplyKeyboardRemove(),
    )

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Requests(ID INT AUTO_INCREMENT PRIMARY KEY NOT NULL, username BIGINT, city VARCHAR(255), category VARCHAR(255), mailing VARCHAR(255))")
    conn.commit()

@my_router.message(Command("cancel"))
@my_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer("команда, чтобы Бот рассылал сообщения /send_messages")


@my_router.message(Form.username)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.from_user.id)
    await state.set_state(Form.mail_rass)
    await message.answer(
        f"Приятно познакомится, {html.quote(message.text)}!\nХотите ли Вы подписаться на рассылку, чтобы прочитать новые объявления сразу?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Yes"),
                    KeyboardButton(text="No"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@my_router.message(Form.mail_rass, F.text.casefold() == "yes")
async def process_agree(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.filter_city)
    await state.update_data(mail_rass=message.text)
    await message.reply(
        "Круто! Теперь давай зададим фильтр для аренды помещения\nВ каком городе Вы хотите арендовать?",
        reply_markup=ReplyKeyboardRemove(),
    )


@my_router.message(Form.mail_rass, F.text.casefold() == "no")
async def process_not_agree(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.filter_city)
    await state.update_data(mail_rass=message.text)
    await message.answer(
        "Я Вас понял.\nДавайте выберем в каком городе Вы хотите арендовать?",
        reply_markup=ReplyKeyboardRemove(),
    )
    

@my_router.message(Form.mail_rass)
async def process_unknown(message: Message) -> None:
    await message.reply("Я Вас не понимаю :(")

@my_router.message(Form.filter_city)
async def process_city(message: Message, state: FSMContext) -> None:
    await state.update_data(filter_city=message.text)
    await state.set_state(Form.filter_category)
    await message.answer(
        "Какой тип помещения хотите арендовать: квартира или комната?",
        reply_markup=ReplyKeyboardRemove(),
    )

@my_router.message(Form.filter_category)
async def process_category(message: Message, state: FSMContext) -> None:
    data = await state.update_data(filter_category=message.text)
    await message.answer("Отлично! Сейчас проанализирую и отправлю доступные помещения")
    
    await show_summary(message=message, data=data)

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    name = str(data["username"])
    category = data["filter_category"]
    city = data["filter_city"]
    mailing = data.get("mail_rass", "<something unexpected>")
    text = f"Вы "
    text += (
        f"хотите арендовать в {html.quote(city)}, в помещении типа - {html.quote(category)}, и на рассылку вы подписались? {html.quote(mailing)}"
        if positive
        else "иначе я Вас не понял..."
    )
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

    cursor = conn.cursor()
    cursor.execute("""INSERT INTO Requests(username, city, category, mailing) VALUES (%s, %s, %s, %s)""", ({html.quote(name)}, {html.quote(city)}, {html.quote(category)}, {html.quote(mailing)}) )
    conn.commit()
    await message.answer("Ответ записан")
    await get_condition_from_db(message=message, data=data)


async def get_condition_from_db(message: Message, data: Dict[str, Any]) -> None:
        await message.answer("Вот список доступных по Вашим условиям:")
        cursor = conn.cursor()
        #cursor.execute("SELECT * FROM app_rent, Requests WHERE app_rent.city = Requests.(%s) AND app_rent.category = Requests.(%s)", {html.quote(city)}, {html.quote(category)})
        cursor.execute("""SELECT a.title, a.city, a.location, a.area, a.floor, a.room, a.price, a.full_description, a.status, r.city, r.category, c.title
                       FROM Estate_db.Requests r, Estate_db.app_rent a, Estate_db.app_categories c
                       WHERE r.city = a.city AND c.title = r.category AND a.status = 'free' 
                       order by r.ID desc limit 1"""
                       )
        
        result = cursor.fetchall()
        if result != '':
            formatted_text = ' '
            for row in result:
                formatted_text = f"Название: {row[0]}\n\n Город: {row[1]}, Улица: {row[2]}, Площадь: {row[3]} кв.м., Этаж: {row[4]}, Комната: {row[5]}\n Цена: {row[6]}\n\n Описание: {row[7]}\n\n Доступность помещения: {row[8]}"
                await message.answer(str(formatted_text))
        else:
            await message.answer("По Вашему запросу такие объявления отсутствуют")   
            cursor.close()
        await message.answer("рассылка по команде /cancel")

#@my_router.message(Command("Send_msg_mail"))
#def telegram_bot_sendtext(bot_message):
#    bot_token = os.environ.get("TOKEN")
#    bot_chatID = os.environ.get("bot_chatID")
#    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=HTML&text=' + bot_message
#    response = request.get(send_text)

def get_message():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='Estate_db',
                                             user='root',
                                             password='root')

        sql_select_query = """select text from messages order by rand() limit 1"""
        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        message = records[0][0]
    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

    return message

async def send_message():
    while True:
        await asyncio.sleep(10) #Время отправления рассылок 10 секунд, можно менять на 3600 - будет раз в час рассылки
        message = get_message()
        cursor = conn.cursor()
        cursor.execute("""SELECT username FROM Estate_db.Requests WHERE mailing='yes' ORDER BY id DESC LIMIT 1""")
        user_id = cursor.fetchone()

        await bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN) #рассылает именно по этому 5554... id, нужно сделать так, чтобы вытаскивалась из бд username


@my_router.message(Command('send_messages'))
async def send_messages_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Рассылка сообщений была начата!")
    await send_message()


#Вытаскивание из базы данных доступных помещений
@my_router.message(Command("list_rent"))
async def get_list_rent_handler(message: types.Message):
    await message.answer("Список доступных помещений")
    #cursor — это объект в памяти вашего компьютера с методами для проведения SQL команд, хранения итогов их выполнения
    cursor = conn.cursor()

    cursor.execute("SELECT title, city, location, area, floor, room, price, full_description, status FROM app_rent")

    result = cursor.fetchall()
    formatted_text = ' '
    for row in result:
        formatted_text = f"Название: {row[0]}\n\n Город: {row[1]}, Улица: {row[2]}, Площадь: {row[3]} кв.м., Этаж: {row[4]}, Комната: {row[5]}\n Цена: {row[6]}\n\n Описание: {row[7]}\n\n Доступность помещения: {row[8]}"
        await message.answer(str(formatted_text))
        
    cursor.close()

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(my_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())