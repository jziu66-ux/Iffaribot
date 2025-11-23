# main.py
import os
import sys
from flask import Flask, request, abort
import telebot
from telebot import types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_URL")  # misol: https://iffaribot.onrender.com

if not TOKEN:
    sys.stderr.write("[ERROR] TELEGRAM_BOT_TOKEN topilmadi. Render -> Environment -> Add variable -> TELEGRAM_BOT_TOKEN\n")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

# === ASOSIY /start HANDLER ===
@bot.message_handler(commands=["start"])
def start_handler(message):
    user = message.from_user
    text = f"👋 Salom, {user.first_name}!\nMen — <b>Iffaribot</b>.\nQuyidagi menyudan bo'lim tanlang 👇"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🆕 Yangi mijoz qo'shish")
    markup.row("⚡ Tezkor savdo")
    markup.row("📦 Tovarlar")
    markup.row("📊 Hisobotlar", "👥 Mijozlar ro'yxati")
    markup.row("⚙️ Sozlamalar")
    bot.send_message(message.chat.id, text, reply_markup=markup)

# (Siz keyinchalik shu yerga boshqa handlerlarni qo'shasiz: yangi mijoz, tezkor savdo va hokazo.)

# === TELEGRAM WEBHOOK ROUTE ===
@app.route("/", methods=["GET"])
def root():
    return "Iffaribot is running."

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        try:
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
        except Exception as e:
            # log qilamiz
            print("Webhook processing error:", e)
            abort(500)
        return "", 200
    else:
        abort(403)

# === Webhookni sozlash (server ishga tushganda) ===
def setup_webhook():
    if WEBHOOK_BASE:
        webhook_url = WEBHOOK_BASE.rstrip("/") + f"/webhook/{TOKEN}"
        try:
            bot.remove_webhook()
            success = bot.set_webhook(url=webhook_url)
            print("Set webhook:", success, webhook_url)
        except Exception as e:
            print("Webhook set error:", e)

if __name__ == "__main__":
    # Renderda portni quyidagicha oling
    port = int(os.environ.get("PORT", "5000"))
    setup_webhook()
    # Flask run (render ushbu portni tekshiradi)
    app.run(host="0.0.0.0", port=port)