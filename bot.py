import telebot
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# توکن بات تلگرام خود را وارد کنید
TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# تابع برای جستجو و دانلود آهنگ از سایت behtamusic.ir
def search_song_on_behtamusic(query):
    # استفاده از quote_plus برای کدگذاری مناسب فارسی در URL
    encoded_query = quote_plus(query)  
    search_url = f"https://behtamusic.ir/?s={encoded_query}"  # سایت behtamusic.ir
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        # چاپ محتویات صفحه برای دیباگ
        print(response.text)  # نمایش HTML

        soup = BeautifulSoup(response.text, 'html.parser')
        song_links = soup.find_all('a', class_='entry-title')  # باید کلاس صحیح را از HTML پیدا کنید

        songs = []
        for link in song_links:
            song_title = link.get_text()
            song_url = link.get('href')
            songs.append((song_title, song_url))

        return songs
    except Exception as e:
        print(f"Error during search: {e}")
        return []

# دکمه‌ها و پیام خوش‌آمدگویی
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn1 = telebot.types.KeyboardButton("جستجو آهنگ")
    markup.add(btn1)
    bot.send_message(message.chat.id, "سلام! برای جستجوی آهنگ، دکمه 'جستجو آهنگ' رو فشار بده.", reply_markup=markup)

# وقتی کاربر دکمه "جستجو آهنگ" رو می‌زنه
@bot.message_handler(func=lambda message: message.text == "جستجو آهنگ")
def ask_for_song_name(message):
    bot.send_message(message.chat.id, "اسم آهنگ یا خواننده رو وارد کن تا جستجو کنم.")

# جستجو و نمایش نتایج جستجو
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    query = message.text.strip()

    bot.send_message(chat_id, "در حال جستجو، لطفاً صبر کنید...")

    # جستجو در سایت behtamusic.ir
    songs = search_song_on_behtamusic(query)

    if not songs:
        bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
        return

    # نمایش لیست آهنگ‌ها
    response = "آهنگ‌های پیدا شده:\n"
    for i, song in enumerate(songs, 1):
        response += f"{i}. {song[0]}\n"
    response += "\nشماره آهنگ مورد نظر رو بفرست تا دانلود بشه."

    bot.send_message(chat_id, response)

# وقتی کاربر شماره آهنگ رو می‌فرسته
@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_song_selection(message):
    chat_id = message.chat.id
    index = int(message.text) - 1

    # جستجو دوباره برای دریافت لینک آهنگ
    query = message.text.strip()
    songs = search_song_on_behtamusic(query)

    if 0 <= index < len(songs):
        song = songs[index]
        song_url = song[1]
        bot.send_message(chat_id, f"در حال دانلود: {song[0]}")
        
        # ارسال لینک دانلود
        bot.send_message(chat_id, f"لینک آهنگ: {song_url}")

    else:
        bot.send_message(chat_id, "شماره وارد شده صحیح نیست.")
bot.remove_webhook()
bot.infinity_polling()
