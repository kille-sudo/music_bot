import telebot
import yt_dlp
import os

TOKEN = '7909038781:AAHpi139qdAatRgj0OvQVmIDjDsHhCcuhW8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! اسم آهنگ یا لینک یوتیوب رو بفرست تا بگردم برات بیارم.")

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    query = message.text.strip()

    if query.startswith("http"):
        url = query
    else:
        url = f"ytsearch:{query}"

    bot.reply_to(message, "در حال جستجو، لطفاً صبر کن...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit('.', 1)[0] + '.mp3'

        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)

        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"خطا پیش اومد: {e}")

bot.infinity_polling()
