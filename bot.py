import requests
import yt_dlp
import telebot
from telebot import types
import re
import os

TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# ذخیره لیست نتایج هر کاربر
user_results = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    # ارسال دکمه برای جستجو
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("جستجوی آهنگ")
    item2 = types.KeyboardButton("جستجوی خواننده")
    markup.add(item1, item2)

    bot.send_message(message.chat.id, "سلام! برای جستجو بر روی دکمه‌ها کلیک کن!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "جستجوی آهنگ" or message.text == "جستجوی خواننده")
def ask_for_search(message):
    # درخواست از کاربر برای وارد کردن اسم آهنگ یا خواننده
    bot.send_message(message.chat.id, "لطفاً نام آهنگ یا خواننده را وارد کن:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # بررسی اینکه آیا این یک لینک یوتیوب است یا نه
    if "youtube.com" in text or "youtu.be" in text:
        bot.send_message(chat_id, "در حال پردازش لینک یوتیوب...")

        try:
            # استفاده از yt-dlp برای دانلود آهنگ از یوتیوب
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                title = info['title']
                filename = f"downloads/{info['id']}.mp3"

                if os.path.exists(filename):
                    with open(filename, 'rb') as audio:
                        bot.send_audio(chat_id, audio, title=title)
                    os.remove(filename)
                else:
                    bot.send_message(chat_id, "دانلود انجام نشد.")
        except Exception as e:
            bot.send_message(chat_id, f"خطا در دانلود: {e}")

    elif chat_id in user_results and text.isdigit():
        # اگر عدد فرستاده بود یعنی انتخاب آهنگه
        index = int(text) - 1
        results = user_results[chat_id]
        if 0 <= index < len(results):
            video = results[index]
            title = video.get('title').replace('/', '_').replace('\\', '_')
            url = video.get('webpage_url')
            filename = f"{title}.mp3"

            bot.send_message(chat_id, f"در حال دانلود: {title}")
            try:
                # دانلود و ارسال آهنگ به کاربر
                response = requests.get(url)
                if response.status_code == 200:
                    bot.send_audio(chat_id, response.content)
                else:
                    bot.send_message(chat_id, "دانلود انجام نشد.")
            except Exception as e:
                bot.send_message(chat_id, f"خطا در دانلود: {e}")
        else:
            bot.send_message(chat_id, "شماره وارد شده معتبر نیست.")
    else:
        # نمایش پیامی که ربات در حال جستجو است
        bot.send_message(chat_id, "در حال جستجو برای آهنگ‌ها...")
        
        query = f"{text} site:youtube.com"  # جستجو در یوتیوب
        url = f"https://www.google.com/search?q={query}"
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('h3', class_='r')
            if not results:
                bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
                return

            user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

            response = "۵ آهنگ پیشنهادی:\n"
            for i, entry in enumerate(results[:5], 1):  # فقط 5 نتیجه اول
                title = entry.get_text()
                response += f"{i}. {title}\n"
            response += "\nشماره آهنگ مورد نظر رو بفرست تا دانلود شه."
            bot.send_message(chat_id, response)
        except Exception as e:
            bot.send_message(chat_id, f"خطا در جستجو: {e}")

bot.infinity_polling()
