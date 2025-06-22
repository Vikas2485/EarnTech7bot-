import telebot
import os
import json

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
INSTAGRAM_LINK = os.getenv("INSTAGRAM_LINK")

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
    if not is_user_joined(message.chat.id):
        join_message = f"🔒 Please join our channel and Instagram to use this bot:\n📢 {CHANNEL_ID}\n📸 {INSTAGRAM_LINK}"
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ Joined", callback_data="check_join"))
        bot.send_message(message.chat.id, join_message, reply_markup=markup)
        return

    if user_id not in users:
        users[user_id] = {"balance": 10, "referrals": 0, "upi": "", "redeemed": False}
        save_users()
        bot.send_message(message.chat.id, "🎉 Welcome to EarnTech7Bot!\nYou received Rs.10 as a welcome bonus using code ECASH10!")
    else:
        bot.send_message(message.chat.id, "👋 Welcome back to EarnTech7Bot!")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Bonus", "👥 Refer")
    markup.row("💼 Profile", "💸 Withdraw")
    bot.send_message(message.chat.id, "👇 Choose an option:", reply_markup=markup)

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_user_joined(call.message.chat.id):
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Please join first.")

@bot.message_handler(func=lambda m: m.text == "💼 Profile")
def profile(message):
    user = users.get(str(message.chat.id), {})
    balance = user.get("balance", 0)
    refs = user.get("referrals", 0)
    bot.send_message(message.chat.id, f"👤 Profile Info:\n💰 Balance: Rs.{balance}\n👥 Referrals: {refs}")

@bot.message_handler(func=lambda m: m.text == "💸 Withdraw")
def withdraw(message):
    bot.send_message(message.chat.id, "💳 Please enter your UPI ID:")
    bot.register_next_step_handler(message, collect_upi)

def collect_upi(message):
    upi = message.text.strip()
    user_id = str(message.chat.id)
    users[user_id]["upi"] = upi
    save_users()
    bot.send_message(message.chat.id, f"✅ UPI set: {upi}\n💰 Now enter the amount to withdraw (Minimum Rs.50):")
    bot.register_next_step_handler(message, process_withdraw)

def process_withdraw(message):
    try:
        amount = float(message.text)
        user_id = str(message.chat.id)
        balance = users[user_id]["balance"]
        if amount < 50:
            bot.send_message(message.chat.id, "❌ Minimum withdraw is Rs.50.")
        elif amount > balance:
            bot.send_message(message.chat.id, "❌ Insufficient balance.")
        else:
            users[user_id]["balance"] -= amount
            save_users()
            bot.send_message(message.chat.id, "📤 Withdrawal Request Received!\nYour request has been submitted.\n💳 As soon as funds are available, your payment will be processed.")
    except:
        bot.send_message(message.chat.id, "❌ Invalid amount.")

bot.polling()
