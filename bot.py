import asyncio
import logging
import os
from aiohttp import request
import pymysql
from typing import Any, Dict
from aiogram import Bot, Dispatcher, html, types, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

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
    cursor.execute("CREATE TABLE IF NOT EXISTS Requests(ID INT AUTO_INCREMENT PRIMARY KEY NOT NULL, username VARCHAR(255), city VARCHAR(255), category VARCHAR(255), mailing VARCHAR(255))")
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


@my_router.message(Form.username)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.text)
    await state.set_state(Form.mail_rass)
    await message.answer(
        f"Приятно познакомится, {html.quote(message.text)}!\nХотите ли Вы подписаться на рассылку?",
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
    #global username
    #username = message.from_user.id
    #cursor = conn.cursor()
    #cursor.execute("""INSERT INTO Requests(username) VALUES (%s)""", (username))
    #conn.commit()

@my_router.message(Form.mail_rass, F.text.casefold() == "yes")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.filter_city)
    await state.update_data(mail_rass=message.text)
    await message.reply(
        "Круто! Теперь давай зададим фильтр для аренды помещения\nВ каком городе Вы хотите арендовать?",
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer("Хотите ли посмотреть список доступных помещений /list_rent")
    #cursor = conn.cursor()
    #cursor.execute("""INSERT INTO Requests(mailing) VALUES (%s)""", {html.quote(message.text)} )
    #conn.commit()

@my_router.message(Form.mail_rass, F.text.casefold() == "no")
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.filter_city)
    await state.clear()
    await message.answer(
        "Я Вас понял.\nДавайте выберем в каком городе Вы хотите арендовать?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer("Хотите ли посмотреть список доступных помещений /list_rent")
    #cursor = conn.cursor()
    #cursor.execute("""INSERT INTO Requests(mailing) VALUES (%s)""", {html.quote(message.text)} )
    #conn.commit()

@my_router.message(Form.mail_rass)
async def process_unknown_write_bots(message: Message) -> None:
    await message.reply("Я Вас не понимаю :(")

@my_router.message(Form.filter_city)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(filter_city=message.text)
    await state.set_state(Form.filter_category)
    await message.answer(
        "Какой тип помещения хотите арендовать: квартира или комната?",
        reply_markup=ReplyKeyboardRemove(),
    )

    #cursor = conn.cursor()
    #cursor.execute("""INSERT INTO Requests(city) VALUES (%s)""", {html.quote(message.text)})
    ##conn.commit() метод фиксирует текущую транзакцию.
    #conn.commit()

@my_router.message(Form.filter_category)
async def process_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(filter_category=message.text)
    await message.answer("Отлично! Сейчас проанализирую и отправлю доступные помещения")
    
    await show_summary(message=message, data=data)
    

async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    name = data["username"]
    category = data["filter_category"]
    city = data["filter_city"]
    mailing = data.get("mail_rass", "<somethong unespected>")
    text = f"Вы, {html.quote(name)}, "
    text += (
        f" хотите арендовать в {html.quote(city)}, в помещении типа - {html.quote(category)}, и на рассылку вы подписались? {html.quote(mailing)}"
        if positive
        else "иначе я Вас не понял..."
    )
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

    cursor = conn.cursor()
    cursor.execute("""INSERT INTO Requests(username, city, category, mailing) VALUES (%s, %s, %s, %s)""", ({html.quote(name)}, {html.quote(city)}, {html.quote(category)}, {html.quote(mailing)}) )
    conn.commit()
    await message.answer("Ответ записан")
    await get_condition_from_db(message=message, data=data)

async def get_condition_from_db(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
        category = data["filter_category"]
        city = data["filter_city"]
        await message.answer("Вот список доступных Вам:")
        cursor = conn.cursor()
        #cursor.execute("SELECT * FROM app_rent, Requests WHERE app_rent.city = Requests.(%s) AND app_rent.category = Requests.(%s)", {html.quote(city)}, {html.quote(category)})
        cursor.execute("SELECT title, city, location, area, floor,  room, price, full_description, status FROM app_rent WHERE status = free INTERSECT SELECT city, room FROM Requests")
        result = cursor.fetchone()
        formatted_text = ' '
        for row in result:
            formatted_text = f"Название: {row[0]}\n\n Город: {row[1]}, Улица: {row[2]}, Площадь: {row[3]} кв.м., Этаж: {row[4]}, Комната: {row[5]}\n Цена: {row[6]}\n\n Описание: {row[7]}\n\n Доступность помещения: {row[8]}"
            await message.answer(str(formatted_text))
        cursor.close()

#def telegram_bot_sendtext(bot_message):
#    bot_token = os.environ.get("bot_token")
#    bot_chatID = os.environ.get("bot_chatID")
#    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=HTML&text=' + bot_message
#    response = request.get(send_text)

@my_router.message()
async def report_db(message: types.Message):
    condition = get_condition_from_db()
    if condition:
        await message.reply(condition)
    else:
        await message.reply("Такого объявления пока нет")


#Вытаскивание из базы данных доступных помещений
@my_router.message(Command("list_rent"))
async def get_list_rent_handler(message: types.Message):
    await message.answer("Список доступных помещений")
    #cursor — это объект в памяти вашего компьютера с методами для проведения SQL команд, хранения итогов их выполнения
    cursor = conn.cursor()

    cursor.execute("SELECT title, city, location, area, floor,  room, price, full_description, status FROM app_rent")

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