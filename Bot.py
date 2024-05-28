from __future__ import print_function
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import asyncio
import datetime

from mysql.connector import connect, Error


bot = Bot(token='2018100064:AAEY-AybuFG4x4YDU_cyBKdKR0Yf3s33WT4')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(Text(equals="Начать"))
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Создать ссылку"))
    chat_id = message.chat.id
    print(message.text)
    mydb = connect(
        host="localhost",
        user="root",
        password="Tractor!337",
        database="bot"
    )
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM referals WHERE chat_id={chat_id}")
    result = mycursor.fetchall()

    await bot.send_message(message.chat.id, "Привет", reply_markup=keyboard)

    if len(result) == 0:
        print("Добавлена новая запись")
        mycursor.execute(f"INSERT INTO referals VALUES ({chat_id}, 0, 0)")
        mydb.commit()
    else:
        print(result[0])
        if result[0][1] != 0 and result[0][2] == 0:
            inline_keyboard = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton('Я подписался', callback_data='subscribed'))
            await bot.send_message(message.chat.id, "Переход по реферальной ссылке засчитан! \n "
                                                    "Осталось только подписаться на наш канал: https://t.me/gfthbvg",
                                   reply_markup=inline_keyboard)
        elif result[0][1] != 0 and result[0][2] == 1:
            await bot.send_message(message.chat.id, "Переход по реферальной ссылке засчитан! \n "
                                                    "Спасибо за подписку на канал!")

    if len(list(map(str, message.text.split(" ")))) == 2:
        invited_by = list(map(str, message.text.split(" ")))[1]
        mycursor.execute(f"SELECT * FROM referals WHERE chat_id={chat_id}")
        result = mycursor.fetchall()
        if result[0][1] == 0:
            mycursor.execute(f"DELETE FROM referals WHERE chat_id={chat_id}")
            mycursor.execute(f"INSERT INTO referals VALUES ({chat_id}, {invited_by}, 0)")
            mydb.commit()
            inline_keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Я подписался', callback_data='subscribed'))
            await bot.send_message(message.chat.id, "Переход по реферальной ссылке засчитан! \n "
                                                    "Осталось только подписаться на наш канал: https://t.me/gfthbvg", reply_markup=inline_keyboard)

    mydb.close()


@dp.callback_query_handler(lambda c: c.data == 'subscribed')
async def process_callback_subscribed(callback_query: types.CallbackQuery):
    #await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_channel_status = await bot.get_chat_member(chat_id='@gfthbvg', user_id=user_id)
    print(user_channel_status)
    if user_channel_status.status != 'left':
        await bot.send_message(callback_query.from_user.id, 'Вы подписались!')
        mydb = connect(
            host="localhost",
            user="root",
            password="Tractor!337",
            database="bot"
        )
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM referals WHERE chat_id={user_id}")
        result = mycursor.fetchall()
        invited_by = result[0][1]
        mycursor.execute(f"DELETE FROM referals WHERE chat_id={user_id}")
        mycursor.execute(f"INSERT INTO referals VALUES ({user_id}, {invited_by}, 1)")
        mydb.commit()
        mydb.close()
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не подписались!')

@dp.message_handler(Text(equals="Создать ссылку"))
async def cmd_start(message: types.Message):
    link = "https://t.me/TeskisBot?start=" + str(message.chat.id)
    await bot.send_message(message.chat.id, f"Ваша реферальная ссылка: {link}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)