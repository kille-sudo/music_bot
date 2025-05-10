import telebot
import yt_dlp
import os

TOKEN = '7909038781:AAHpi139qdAatRgj0OvQVmIDjDsHhCcuhW8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "سلام! اسم آهنگ رو بفرست تا از یوتیوب برات MP3 بفرستم.")

@bot.message_handler(func=lambda message: True)
def download_mp3(message):
    query = f"ytsearch:{message.text}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    bot.send_message(message.chat.id, f"در حال جستجو و دانلود: {message.text}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        audio = open('song.mp3', 'rb')
        bot.send_audio(message.chat.id, audio)
        audio.close()
        os.remove("song.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"خطا در دانلود: {e}")

bot.infinity_polling()
