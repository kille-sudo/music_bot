import telebot
import requests
import json

TOKEN = '7909038781:AAHLie4sdqWGgaKxeuIYqkMnYQEiTAbsfJY'
bot = telebot.TeleBot(TOKEN)

# ذخیره لیست نتایج هر کاربر
user_results = {}

# سایت‌های مختلف برای جستجو
def search_music(query):
    results = []
    
    # جستجو در سایت‌های ایرانی
    # جستجو در RadioJavan
    try:
        radiojavan_url = f"https://www.radiojavan.com/api/v1/search?query={query}&type=track"
        response = requests.get(radiojavan_url)
        data = response.json()
        results.extend(data['data']['tracks'])  # نتایج موسیقی از RadioJavan
    except Exception as e:
        print(f"خطا در جستجو در RadioJavan: {e}")
    
    # جستجو در SoundCloud
    try:
        soundcloud_url = f"https://api.soundcloud.com/tracks?client_id=YOUR_SOUNDCLOUD_CLIENT_ID&q={query}"
        response = requests.get(soundcloud_url)
        soundcloud_data = response.json()
        results.extend(soundcloud_data)  # نتایج موسیقی از SoundCloud
    except Exception as e:
        print(f"خطا در جستجو در SoundCloud: {e}")
    
    # جستجو در Jamendo
    try:
        jamendo_url = f"https://api.jamendo.com/v3.0/tracks/?client_id=YOUR_JAMENDO_CLIENT_ID&search={query}"
        response = requests.get(jamendo_url)
        jamendo_data = response.json()
        results.extend(jamendo_data['results'])  # نتایج موسیقی از Jamendo
    except Exception as e:
        print(f"خطا در جستجو در Jamendo: {e}")
    
    return results

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
            track = results[index]
            title = track.get('title')
            url = track.get('url')
            
            bot.send_message(chat_id, f"آهنگ مورد نظر: {title}\nلینک: {url}")
        else:
            bot.send_message(chat_id, "شماره وارد شده معتبر نیست.")
    else:
        # جستجو برای آهنگ‌ها
        query = text
        results = search_music(query)

        if not results:
            bot.send_message(chat_id, "هیچ آهنگی پیدا نشد.")
            return

        user_results[chat_id] = results  # ذخیره نتایج برای انتخاب بعدی

        response_text = "۵ آهنگ پیشنهادی:\n"
        for i, track in enumerate(results[:5], 1):
            response_text += f"{i}. {track.get('title')}\n"
        response_text += "\nشماره آهنگ مورد نظر رو بفرست تا لینک رو دریافت کنی."
        bot.send_message(chat_id, response_text)

bot.infinity_polling()
