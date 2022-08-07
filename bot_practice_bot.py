from pyrogram import Client, filters
from pyrogram.filters import chat
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
import time
import pytz
from datetime import datetime
import apscheduler.schedulers.background


with open('config.txt', 'r') as con:
    con = con.read().split(':')
    api_id = con[0]
    api_hash = con[1]

with open('bot_practice_bot API.txt', 'r') as f:
    api_key = f.read()

bot = Client("bot_practice_bot", api_id=api_id, api_hash=api_hash, bot_token=api_key)


tips_dict = {}
bot.DONE_LIST = set()
bot.COUNTER = set()

@bot.on_callback_query(filters.regex('start'))
async def start(bot: bot, msg: CallbackQuery):
    await msg.answer()
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Write a tip ✍️", callback_data="add_tip")]
        ]
    )
    await msg.message.reply("Start", reply_markup=buttons)

@bot.on_message(filters.command('start'))
async def start(bot, msg):
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Write a tip ✍️", callback_data="add_tip")]
        ]
    )
    await msg.reply("Start", reply_markup=buttons)


@bot.on_callback_query(filters.regex('add_tip'))
async def add_tip(bot: bot, msg: CallbackQuery):
    await msg.answer()
    answer = await bot.ask(msg.from_user.id, 'Add a new tip:')
    tips_dict[answer.text] = [msg.from_user.username]
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🆕 Add a new tip 🆕", callback_data="add_tip")],
            [InlineKeyboardButton('✅ Done writing tips ✅', callback_data="done")]
        ])
    await msg.message.reply("Tip saved", reply_markup=buttons)

bot.ANALISTS_LIST = set()
@bot.on_callback_query(filters.regex("done"))
async def done(bot: bot, msg: CallbackQuery):
    await msg.answer()
    analists_id = open('analists IDS.txt', 'a+')
    bot.ANALISTS_LIST.add(f'{msg.from_user.username} - {msg.from_user.id}')
    analists_id.write('\n'.join(bot.ANALISTS_LIST))
    analists_id.close()
    # print(bot.DONE_LIST, bot.COUNTER)
    bot.DONE_LIST.add(msg.from_user.id)
    if len(bot.DONE_LIST) == 6: # לשנות לפי מספר האנליסטים
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("start evaluate", callback_data="evaluate_tips")]])
        for user in bot.DONE_LIST:
            await bot.send_message(chat_id=user,text="Evaluate menu", reply_markup=buttons)
    else:
        await msg.message.reply('Please wait for everyone to finish')


@bot.on_message(filters.command('admin_help'))
async def admin_help(bot, msg):
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄הפעלת הבוט - המידע נשמר🔄", callback_data="start")],
         [InlineKeyboardButton("✍️הוספת טיפ חדש✍️", callback_data="add_tip")],
         [InlineKeyboardButton("💯דירוג הטיפים השמורים💯", callback_data="evaluate_tips")],
          [InlineKeyboardButton("💾הורדת הקובץ אחרי הדירוג💾", callback_data="download_tips")],
           [InlineKeyboardButton("❌מחיקת כל המידע השמור (טיפים וקובץ)❌", callback_data="delete_tips")]]
         )
    await bot.send_message(msg.from_user.id, text='תפריט אדמין', reply_markup=buttons)


@bot.on_callback_query(filters.regex('evaluate_tips'))
async def evaluate_tips(bot, msg: CallbackQuery):
    await msg.answer()
    aviatar_id = 1925421147
    new_dict = {}
    if len(tips_dict.keys()) == 0:
        await msg.message.reply('No tips to evaluate')
    else:
        for tip, username in tips_dict.items():
            answer = await bot.ask(msg.from_user.id, f'<b>Evaluate this tip</b>:\n{tip}')
            bot.COUNTER.add(msg.from_user.id)
            new_dict = tips_dict.copy()
            new_dict[tip].append(f'{msg.from_user.username} - {answer.text}')

        with open("graded tips backup.txt", 'w', encoding='utf-8') as file:
            # sorted_dict = {k: v for k, v in sorted(new_dict.items(), key=lambda item: item[1])}
            for key, val in new_dict.items():
                all_users = '\n'.join(sorted(val[1:], key=lambda x: x.split('-')[0]))
                file.write(f"Created by: {val[0]}\n{key}\nEvaluations:\n{all_users}\n\n\n")

        with open("graded tips.txt", 'w', encoding='utf-8') as file:
            for key, val in new_dict.items():
                all_users = '\n'.join(sorted(val[1:], key=lambda x: x.split('-')[0]))
                file.write(f"Created by: {val[0]}\n{key}\nEvaluations:\n{all_users}\n\n\n")
            await msg.message.reply('No more tips to evaluate')

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💾 Download tips 💾", callback_data="download_tips")],
            [InlineKeyboardButton('🗑️ Delete tips 🗑️', callback_data="delete_tips")]
        ])
    if bot.COUNTER == bot.DONE_LIST:
        bot.DONE_LIST = set()
        bot.COUNTER = set()
        await bot.send_message(852642452, text='כולם סיימו לדרג', reply_markup=buttons)


@bot.on_callback_query(filters.regex('download_tips'))
async def download_tips(bot, msg: CallbackQuery):
    await msg.answer()
    with open('graded tips.txt', 'r', encoding='utf-8') as d:
        if len(d.read()) != 0:
            await bot.send_document(chat_id=msg.from_user.id, document=d.name)
            # await bot.send_message(msg.from_user.id, '\n/delete_tips תלחץ על זה בשביל לאפס את כל המידע בבוט')
        else:
            await msg.message.reply('הקובץ ריק')


@bot.on_message(filters.command('download_backup_tips'))
async def download_backup_tips(bot, msg):
    with open('graded tips backup.txt', 'r', encoding='utf-8') as d:
        if len(d.read()) != 0:
            await bot.send_document(chat_id=msg.from_user.id, document=d.name)
            new = open('graded tips backup.txt', 'w')
            new.close()
            await msg.reply('קובץ הגיבוי נמחק')
            # await bot.send_message(msg.from_user.id, '\n/delete_tips תלחץ על זה בשביל לאפס את כל המידע בבוט')
        else:
            await msg.reply('הקובץ ריק')


@bot.on_callback_query(filters.regex('delete_tips'))
async def delete_tips(bot, msg: CallbackQuery):
    await msg.answer()
    with open('graded tips.txt', 'w', encoding='utf-8') as d:
        d.close()
    tips_dict.clear()
    await msg.message.reply('המידע שבבוט נמחק')


def evaluate_msg():
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Click here to evaluate", callback_data="evaluate_tips")]])
    for user in bot.DONE_LIST:
        bot.send_message(chat_id=user, text="It's 21:00, please start evaluate tips", reply_markup=buttons)

def add_tip_msg():
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Click here to add tips", callback_data="add_tip")]])
    #sadat, hezi, gil, robin
    analists_list = [454763223, 1395968859, 1578339713, 71700939]
    for user in analists_list:
        bot.send_message(chat_id=user, text="It's 20:00, please write tips", reply_markup=buttons)


scheduler = apscheduler.schedulers.background.BackgroundScheduler()
tz = pytz.timezone('Asia/Jerusalem')
scheduler.add_job(add_tip_msg, 'cron', day_of_week='0-6', hour='20', minute='00', timezone=tz)
scheduler.add_job(evaluate_msg, 'cron', day_of_week='0-6', hour='21', minute='00', timezone=tz)

scheduler.start()


bot.start()
bot.loop.run_forever()
# bot.run()