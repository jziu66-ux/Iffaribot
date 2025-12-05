import os
import logging
from flask import Flask, request, abort

import telebot
from telebot import types

# Log sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokenni faqat muhitdan o'qiymiz
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN topilmadi. Render -> Environment -> Add variable -> TELEGRAM_BOT_TOKEN kiriting.")
    raise SystemExit("TELEGRAM_BOT_TOKEN not set")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

# --- SKELETON HANDLERLAR (Keyingi funksiyalar shu yerga qo'shiladi) ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    txt = "👋 Salom! Men — Iffaribot. Asosiy menyudan bo'lim tanlang."
    bot.send_message(message.chat.id, txt, reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.row("🆕 Yangi mijoz qo'shish", "⚡ Tezkor savdo")
    m.row("📦 Tovarlar", "📊 Hisobotlar")
    m.row("👥 Mijozlar ro'yxati", "⚙️ Sozlamalar")
    return m

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.strip()
    if text == "🆕 Yangi mijoz qo'shish":
        bot.send_message(message.chat.id, "Iltimos, mijoz ismini kiriting 👇")
        # keyingi qadamlar uchun: db-ga yozish (skelet)
        return
    if text == "⚡ Tezkor savdo":
        bot.send_message(message.chat.id, "Tezkor savdo: savdo turini tanlang.", reply_markup=types.ReplyKeyboardMarkup(True).row("⚙️ Ulgurji","🧾 Chakana"))
        return
    # boshqa tugmalarni shu yerga yozamiz
    bot.send_message(message.chat.id, "⚠️ Buyuk funksiya hali yozilmagan. Keyingi qadam uchun admin-ga yozing.")

# --- Flask route: Telegram webhook uchun ---
@app.route("/webhook/" + TOKEN, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "", 200
    else:
        abort(403)

# Healthcheck
@app.route("/", methods=["GET"])
def index():
    return "Iffaribot is up", 200

# Webhook o'rnatish funksiyasi (app ishga tushganda chaqiriladi)
def set_webhook():
    # Agar foydalanuvchi WEBHOOK_URL muhitini qo'ygansa undan foydalanamiz
    webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not webhook_url:
        logger.error("WEBHOOK_URL yoki RENDER_EXTERNAL_URL muhit o'zgaruvchisi topilmadi. Render-da bu avtomatik bo'lmasligi mumkin.")
        return False

    full_url = webhook_url.rstrip("/") + "/webhook/" + TOKEN
    try:
        bot.remove_webhook()
        res = bot.set_webhook(full_url)
        logger.info(f"Set webhook result: {res} -> {full_url}")
        return res
    except Exception as e:
        logger.exception("Webhook o'rnatishda xato:")
        return False

if __name__ == "__main__":
    # Agar lokalda sinov qilayotgan bo'lsangiz: WEBHOOK_URL ni o'rnatib, quyidagilarni ishga tushiring
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))