import logging
import gzdev
from aiogram import Bot, Dispatcher, executor, types, filters
import datetime
import os
from config import TG_TOKEN
import sqlite3
import asyncio
import use_db  # Delete and create tables in SQLite DB. Remove in prod
import keyboards as kb


# API_TOKEN = os.environ.get("tg_token")
API_TOKEN = TG_TOKEN


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_active_subs():

    """
    Function get all active subscribes in DB
    """

    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute("SELECT word, chat_id FROM subscribes WHERE isactive = 1")
    chat_ids = cur.fetchall()
    num = 0
    result = {}
    for item in chat_ids:
        num += 1
        result[num] = item  # Create dict for active subscribes with numbers for keys
    return result


async def get_gz_data(word, uid):
    """
    Get data of Lots in PGZ for subscribe
    """
    result = await gzdev.getLots(name_ru=word.lower())
    if result == {}:
        await bot.send_message(uid, 'Нет лотов содержащих слово: ' + word)
    else:
        if isinstance(result, str):  # If result is str (path to file), send to user file
            await bot.send_document(uid, open(result, "rb"))
        else:  # If result is dict of Lots, send Lots in message
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
    await message.reply("Отправь слово и тебе выйдут все лоты, "
                        "название которых содержат это слово и были изменены после 25.11.2021")


@dp.message_handler(commands=['Подписки'])
async def process_start_command(message: types.Message):
    """
    This handler will be called when user sends `/Подписки` command, and send to user his active subscribes
    """

    await message.reply("Привет!", reply_markup=kb.ReplyKeyboardRemove())
    answer = ''
    subs = get_active_subs()
    for key, item in subs.items():
        answer = answer + '/' + str(key) + '. ' + str(item[0]) + '\n'
    await message.reply(answer, reply_markup=kb.greet_kb)


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^[/,\d]*']))
async def send_welcome(message: types.Message, regexp_command):
    """
    This handler will be called when user sends command like /1, /2 ..., and unsubscribe for this number word
    """
    # TODO realize unsubscribe for word number
    a = message
    a.text = message.text[1:]
    await echo(a)


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['^/*']))
async def send_welcome(message: types.Message, regexp_command):
    """
    This handler will be called when user sends command starts with '/' and call subscribe/unsubscribe on word after '/'
    """

    a = message
    a.text = message.text[1:]
    await echo(a)


@dp.message_handler(commands=['userlog'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/userlog` command and show all subscribes
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
    """
    This handler will be called when user sends any word and create subscribe or unsubscribe on message.text
    """
    print(message.text)
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    uid = message.from_user.id
    uname = message.from_user.username
    user = (uid, uname, True)
    print(user)

    cur.execute("SELECT isactive FROM subscribes WHERE word = (?) AND chat_id=(?);",
                (message.text, message.from_user.id))
    x = cur.fetchall()
    print(x)

    if len(x) == 0:

        isact = True
    else:
        isact = not bool(x[0][0])
    print(isact)
    cur.execute("INSERT OR REPLACE INTO subscribes (word, chat_id, isactive) VALUES(?, ?, ?);",
                (message.text, message.from_user.id, isact))
    if isact:
        await message.answer('Подписка по слову "{word}" оформлена'.format(word=message.text))
    else:
        await message.answer('Подписка по слову "{word}" отменена'.format(word=message.text))
    conn.commit()


async def periodic(sleep_for):
    """
    Function for periodic send data for subscribes
    :param sleep_for:  time between send data for subscribes
    :return:
    """
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

        for item in chat_ids:

            await get_gz_data(item[0], item[1])


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.create_task(periodic(10))
    executor.start_polling(dp, skip_updates=True)
