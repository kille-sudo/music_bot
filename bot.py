import telebot
import yt_dlp
import os
from youtubesearchpython import VideosSearch

TOKEN = '7909038781:AAHpi139qdAatRgj0OvQVmIDjDsHhCcuhW8'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "سلام! اسم آهنگ رو بفرست تا از یوتیوب برات MP3 بفرستم.")

@bot.message_handler(func=lambda message: True)
def get_audio(message):
    query = message.text
    bot.send_message(message.chat.id, f"در حال جستجوی: {query}")

    videosSearch = VideosSearch(query, limit=1)
    results = videosSearch.result()
    if not results['result']:
        bot.send_message(message.chat.id, "آهنگی پیدا نشد.")
        return

    video_url = results['result'][0]['link']
    title = results['result'][0]['title']
    bot.send_message(message.chat.id, f"دانلود از: {title}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        audio = open('song.mp3', 'rb')
        bot.send_audio(message.chat.id, audio)
        audio.close()
        os.remove("song.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"خطا در دانلود: {e}")

bot.infinity_polling()
