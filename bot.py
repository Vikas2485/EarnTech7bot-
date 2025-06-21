import telebot
from config import TOKEN, ADMIN_ID, CHANNEL_ID, INSTAGRAM_LINK
import json

bot = telebot.TeleBot(TOKEN)

users = {}
try:
    with open("data.json", "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open("data.json", "w") as f:
        json.dump(users, f)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {"balance": 10, "referrals": 0, "upi": ""}
        save_users()
        bot.send_message(message.chat.id, "🎉 Welcome to EarnTech7Bot!
You received ₹10 as a welcome bonus using code ECASH10!")
    else:
        bot.send_message(message.chat.id, "👋 Welcome back to EarnTech7Bot!")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Bonus", "👥 Refer")
    markup.row("💼 Profile", "💸 Withdraw")
    bot.send_message(message.chat.id, "👇 Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💼 Profile")
def profile(message):
    user = users.get(str(message.chat.id), {})
    balance = user.get("balance", 0)
    refs = user.get("referrals", 0)
    bot.send_message(message.chat.id, f"👤 Profile Info:
💰 Balance: ₹{balance}
👥 Referrals: {refs}")

@bot.message_handler(func=lambda m: m.text == "💸 Withdraw")
def withdraw(message):
    bot.send_message(message.chat.id, "💳 Please enter your UPI ID:")
    bot.register_next_step_handler(message, collect_upi)

def collect_upi(message):
    upi = message.text.strip()
    user_id = str(message.chat.id)
    users[user_id]["upi"] = upi
    save_users()
    bot.send_message(message.chat.id, f"✅ UPI set: {upi}
💰 Now enter the amount to withdraw (Minimum ₹50):")
    bot.register_next_step_handler(message, process_withdraw)

def process_withdraw(message):
    try:
        amount = float(message.text)
        user_id = str(message.chat.id)
        balance = users[user_id]["balance"]
        if amount < 50:
            bot.send_message(message.chat.id, "❌ Minimum withdraw is ₹50.")
        elif amount > balance:
            bot.send_message(message.chat.id, "❌ Insufficient balance.")
        else:
            users[user_id]["balance"] -= amount
            save_users()
            bot.send_message(message.chat.id, "📤 Withdrawal Request Received!

Your request has been submitted.
💳 As soon as funds are available, your payment will be processed.

🔒 Please be patient – payments will be sent as soon as possible.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid amount.")

bot.polling()