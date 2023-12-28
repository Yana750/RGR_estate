import asyncio
import logging
import pymysql
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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

# Обработка команды /start
@my_router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для аренды недвижимости.")
    await message.answer("Введите ваше имя.")

#Вытаскивание из базы данных доступных помещений
@my_router.message(Command("list_rent"))
async def get_list_rent_handler(message: types.Message):
    await message.answer("Список доступных помещений")
    cursor = conn.cursor()

    cursor.execute("SELECT title, city, location, area, floor,  room, price, full_description, status FROM app_rent")

    result = cursor.fetchall()
    formatted_text = ' '
    for row in result:
        formatted_text = f"Название: {row[0]}\n\n Город: {row[1]}, Улица: {row[2]}, Площадь: {row[3]}, Этаж: {row[4]}, Комната: {row[5]}\n Цена: {row[6]}\n\n Описание: {row[7]}\n\n Доступность помещения: {row[8]}"
        await message.answer(str(formatted_text))
        await message.answer("Для выбора помещения для аренды напишите команду /Renta_reservations")

    cursor.close()

#@my_router.message(Command("Add_rent"))
#async def handle_message(message: types.Message):
#    await message.answer("Введите название объявления. Например, сдам комнату недорого")
#    slug = message.
#    #await message.answer("Введите Ваше день рождение.")
#    #birth_date = message.text
#    #cursor — это объект в памяти вашего компьютера с методами для проведения SQL команд, хранения итогов их выполнения
#    cursor = conn.cursor()
#    cursor.execute("INSERT INTO app_profiles (slug) VALUES (%s)", (slug))
#    conn.commit()

#    await message.reply("Ответ сохранен в базе данных.")


@my_router.message(Command("Add_group"))
async def Add_group_handler(message: types.Message):
    await message.answer("Добавление группы")
    await state.update_data(process_groupps=message.text)
    cursor = conn.cursor()
    sql1="insert into auth_group(name) values(%s)"
    val = {html.quote(message.text)}
    





async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(my_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())