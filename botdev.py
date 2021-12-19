import logging
import gzdev
from aiogram import Bot, Dispatcher, executor, types, filters
import datetime
import os
from config import TG_TOKEN
import sqlite3
import asyncio
import use_db
import keyboards as kb


# API_TOKEN = os.environ.get("tg_token")
API_TOKEN = TG_TOKEN


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_active_subs():
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute("SELECT word, chat_id FROM subscribes WHERE isactive = 1")
    chat_ids = cur.fetchall()
    num = 0
    result = {}
    for id in chat_ids:
        num += 1
        result[num] = id
    return result

async def get_gz_data(word, uid):

    result = await gzdev.getLots(name_ru=word.lower())
    if result == {}:
        await bot.send_message(uid, 'Нет лотов содержащих слово: ' + word)
    else:
        if isinstance(result, str):
            await bot.send_document(uid, open(result, "rb"))
        else:
            for x, y in result.items():
                print(y)
                print(type(y))
                i = await gzdev.parseLots(y)
                await bot.send_message(uid, i)



@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Отправь слово и тебе выйдут все лоты, название которых содержат это слово и были изменены после 25.11.2021")


@dp.message_handler(commands=['Подписки'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!", reply_markup=kb.ReplyKeyboardRemove())
    # conn = sqlite3.connect('tasks.db')
    # cur = conn.cursor()
    # cur.execute("SELECT word, chat_id FROM subscribes WHERE isactive = 1")
    # chat_ids = cur.fetchall()
    # answer = 'Ваши подписки: \n'
    # num = 0
    # result = {}
    # for id in chat_ids:
    #     num += 1
    #     result[num] = id
    #     answer = answer + '/'+ str(num) + ' ' + str(id[0]) + '\n'
    answer = ''
    subs = get_active_subs()
    for key, item in subs.items():
        answer = answer + '/' + str(key) + '. ' + str(item[0]) + '\n'


    await message.reply(answer, reply_markup=kb.greet_kb)


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^[/,\d]*']))
async def send_welcome(message: types.Message, regexp_command):
    a = (message)
    a.text = message.text[1:]
    await echo(a)


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^/*']))
async def send_welcome(message: types.Message, regexp_command):
    a = (message)
    a.text = message.text[1:]
    await echo(a)


@dp.message_handler(commands=['userlog'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM subscribes")
    result = cur.fetchall()
    conn.commit()
    await message.answer("Список подписок:")
    for r in result:
        await message.answer("WORD: {word}, UID: {uid}, ISACTIVE: {isact}".format(word=r[0], uid=r[1], isact=r[2]))




@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    print(message.text)
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    uid = message.from_user.id
    uname = message.from_user.username
    user = (uid, uname, True)
    print(user)
    # Разные таблицы пользователей и слов
    # cur.execute("INSERT OR IGNORE INTO users (userid, username, isactive) VALUES(?, ?, ?);", user)
    # user_id = cur.lastrowid
    # if user_id == 0:
    #     cur.execute("SELECT id FROM users WHERE userid = (?)", (user[0],))
    #     user_id = cur.fetchone()[0]
    # cur.execute("INSERT OR IGNORE INTO key_words (word) VALUES(?);", (message.text,))
    # word_id = cur.lastrowid
    # if word_id == 0:
    #     cur.execute("SELECT id FROM key_words WHERE word = (?)", (message.text,))
    #     word_id = cur.fetchone()[0]
    # print(user_id, word_id)
    # cur.execute("INSERT OR IGNORE INTO user_word (word_id, user_id) VALUES(?, ?);", (word_id, user_id))

    # Одна таблица для пользователей и слов
    cur.execute("SELECT isactive FROM subscribes WHERE word = (?) AND chat_id=(?);", (message.text, message.from_user.id))
    x = cur.fetchall()
    print(x)

    if len(x) == 0:

        isact = True
    else:
        isact = not bool(x[0][0])
    print(isact)
    cur.execute("INSERT OR REPLACE INTO subscribes (word, chat_id, isactive) VALUES(?, ?, ?);", (message.text, message.from_user.id, isact))
    if isact:
        await message.answer('Подписка по слову "{word}" оформлена'.format(word=message.text))
    else:
        await message.answer('Подписка по слову "{word}" отменена'.format(word=message.text))
    conn.commit()

    # Этот код выведен в функцию get_gz_data
    #
    # await message.answer('Начинаю поиск')
    # result = await gzdev.getLots(name_ru=message.text.lower())
    # if result == {}:
    #     await message.answer('Нет лотов содержащих слово: '+message.text)
    # else:
    #     if isinstance(result, str):
    #         await message.answer_document(open(result, "rb"))
    #     else:
    #         for x, y in result.items():
    #             print(y)
    #             print(type(y))
    #             i = await gzdev.parseLots(y)
    #             await message.answer(i)


async def periodic(sleep_for):
    while True:
        await asyncio.sleep(sleep_for)
        now = datetime.datetime.now()
        conn = sqlite3.connect('tasks.db')
        cur = conn.cursor()
        cur.execute("SELECT word, chat_id FROM subscribes WHERE isactive = 1")
        chat_ids = cur.fetchall()
        print(f"{now}")
        print('*'*50)
        print(chat_ids)
        # if chat_ids != []:

        for id in chat_ids:
            # print(id)
            # await bot.send_message(int(id[1]), f"{now}", disable_notification=True)
            await get_gz_data(id[0], id[1])



if __name__ == '__main__':
    # executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(10))
    # dp.loop.create_task(periodic(10))

    executor.start_polling(dp, skip_updates=True)