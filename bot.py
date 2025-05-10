import telebot
import yt_dlp
import os

TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# ذخیره لیست نتایج هر کاربر
user_results = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "سلام! اسم خواننده یا آهنگ رو بفرست تا لیست آهنگ‌هاش رو نشون بدم.")

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
                'cookies': 'all_cookies',  # استفاده از کوکی‌ها
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
        # جستجو برای آهنگ‌ها
        query = f"ytsearch5:{text}"
        ydl_opts = {
            'quiet': True,
            'cookies': 'all_cookies',  # استفاده از کوکی‌ها
            'skip_download': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                results = info.get('entries', [])
                if not results:
                    bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
                    return

                user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

                response = "۵ آهنگ پیشنهادی:\n"
                for i, entry in enumerate(results, 1):
                    response += f"{i}. {entry.get('title')}\n"
                response += "\nشماره آهنگ مورد نظر رو بفرست تا دانلود شه."
                bot.send_message(chat_id, response)
        except Exception as e:
            bot.send_message(chat_id, f"خطا در جستجو: {e}")

bot.infinity_polling()
