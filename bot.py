import telebot
from telebot import types
import yt_dlp
import os
import requests
from bs4 import BeautifulSoup

TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# ذخیره لیست نتایج هر کاربر
user_results = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_search_artist = types.KeyboardButton("جستجوی خواننده")
    item_search_song = types.KeyboardButton("جستجوی آهنگ")
    markup.add(item_search_artist, item_search_song)
    bot.send_message(message.chat.id, "سلام! از اینجا انتخاب کن که بخواهی خواننده یا آهنگ رو جستجو کنی.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "جستجوی خواننده")
def search_by_artist(message):
    bot.send_message(message.chat.id, "اسم خواننده رو وارد کن:")
    bot.register_next_step_handler(message, search_artist)

@bot.message_handler(func=lambda message: message.text == "جستجوی آهنگ")
def search_by_song(message):
    bot.send_message(message.chat.id, "اسم آهنگ رو وارد کن:")
    bot.register_next_step_handler(message, search_song)

def search_artist(message):
    artist = message.text.strip()
    chat_id = message.chat.id

    # پیامی که نشان دهد ربات در حال جستجو است
    bot.send_message(chat_id, "در حال جستجو... لطفاً صبور باشید.")

    # جستجو برای آهنگ‌های خواننده
    query = f"ytsearch5:{artist} music"
    ydl_opts = {'quiet': True, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            results = info.get('entries', [])
            if not results:
                bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
                return

            user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

            # ارسال دکمه‌ها برای انتخاب آهنگ
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i, entry in enumerate(results[:5], 1):  # نمایش 5 آهنگ اول
                item = types.KeyboardButton(f"{i}. {entry.get('title')}")
                markup.add(item)
            item_back = types.KeyboardButton("بازگشت")
            markup.add(item_back)

            bot.send_message(chat_id, f"آهنگ‌های {artist}:\nانتخاب کنید:", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"خطا در جستجو: {e}")

def search_song(message):
    song = message.text.strip()
    chat_id = message.chat.id

    # پیامی که نشان دهد ربات در حال جستجو است
    bot.send_message(chat_id, "در حال جستجو... لطفاً صبور باشید.")

    # جستجو برای آهنگ
    query = f"ytsearch5:{song} music"
    ydl_opts = {'quiet': True, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            results = info.get('entries', [])
            if not results:
                bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
                return

            user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

            # ارسال دکمه‌ها برای انتخاب آهنگ
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i, entry in enumerate(results[:5], 1):  # نمایش 5 آهنگ اول
                item = types.KeyboardButton(f"{i}. {entry.get('title')}")
                markup.add(item)
            item_back = types.KeyboardButton("بازگشت")
            markup.add(item_back)

            bot.send_message(chat_id, f"آهنگ‌های مرتبط با '{song}':\nانتخاب کنید:", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"خطا در جستجو: {e}")

@bot.message_handler(func=lambda message: message.text.isdigit())
def download_song(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # اگر عدد فرستاده بود یعنی انتخاب آهنگه
    if chat_id in user_results:
        index = int(text) - 1
        results = user_results[chat_id]
        if 0 <= index < len(results):
            video = results[index]
            title = video.get('title').replace('/', '_').replace('\\', '_')
            url = video.get('webpage_url')
            filename = f"{title}.mp3"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': filename.replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'cookies':'all_cookies.txt',
            }

            bot.send_message(chat_id, f"در حال دانلود: {title}")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(filename):
                    with open(filename, 'rb') as audio:
                        bot.send_audio(chat_id, audio, title=title)
                    os.remove(filename)
                else:
                    bot.send_message(chat_id, "دانلود انجام نشد.")
            except Exception as e:
                bot.send_message(chat_id, f"خطا در دانلود: {e}")
        else:
            bot.send_message(chat_id, "شماره وارد شده معتبر نیست.")
    else:
        bot.send_message(chat_id, "لطفاً ابتدا جستجو کنید.")

@bot.message_handler(func=lambda message: message.text == "بازگشت")
def go_back(message):
    # اگر کاربر دکمه "بازگشت" را بزند
    welcome(message)

bot.infinity_polling()
