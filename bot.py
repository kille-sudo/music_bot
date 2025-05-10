import telebot
import yt_dlp
import os
import urllib.parse
from telebot import types

TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# ذخیره لیست نتایج هر کاربر
user_results = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    # ساخت دکمه‌ها
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    search_button = types.KeyboardButton("جستجوی آهنگ")
    markup.add(search_button)
    
    bot.send_message(message.chat.id, "سلام! برای جستجوی آهنگ، روی دکمه زیر کلیک کن.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "جستجوی آهنگ")
def handle_search(message):
    # ایجاد دکمه‌های inline برای وارد کردن نام خواننده یا آهنگ
    markup = types.ReplyKeyboardRemove()  # حذف کیبورد قبلی
    bot.send_message(message.chat.id, "لطفا نام خواننده یا آهنگ رو وارد کن.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # اگر عدد فرستاده بود یعنی انتخاب آهنگه
    if chat_id in user_results and text.isdigit():
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
        # ارسال پیام "در حال جستجو..."
        bot.send_message(chat_id, "در حال جستجوی آهنگ‌ها...")

        # تبدیل متنی که به فارسی وارد شده به URL مناسب
        query = urllib.parse.quote(text)  # تبدیل نام خواننده یا آهنگ به URL ایمن
        query = f"ytsearch5:{query}"  # جستجو فقط برای ۵ نتیجه
        ydl_opts = {'quiet': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                results = info.get('entries', [])
                if not results:
                    bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
                    return

                user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

                response = "۵ آهنگ پیشنهادی:\n"  # نمایش فقط ۵ آهنگ
                for i, entry in enumerate(results, 1):
                    response += f"{i}. {entry.get('title')}\n"
                response += "\nشماره آهنگ مورد نظر رو بفرست تا دانلود شه."
                bot.send_message(chat_id, response)
        except Exception as e:
            bot.send_message(chat_id, f"خطا در جستجو: {e}")

bot.remove_webhook()
bot.infinity_polling()
