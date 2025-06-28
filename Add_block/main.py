import telebot
from config import token
import time

bot = telebot.TeleBot(token)

user_messages = {}

# Ограничения
FLOOD_LIMIT = 5        
FLOOD_SECONDS = 10     

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления чатом.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status

        if user_status in ['administrator', 'creator']:
            bot.reply_to(message, "Невозможно забанить администратора или создателя.")
        else:
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение.")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    bot.send_message(message.chat.id, 'Привет я бот-менеджер этого чата!')
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or f'id{user_id}'
    text = message.text.lower()

    user_status = bot.get_chat_member(chat_id, user_id).status

    
    now = time.time()
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t <= FLOOD_SECONDS]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > FLOOD_LIMIT:
        if user_status not in ['administrator', 'creator']:
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"Пользователь @{username} был забанен за флуд.")
            return

    # Удаление рекламы
    if "переходи" in text or "жми" in text:
        if user_status not in ['administrator', 'creator']:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"Сообщение @{username} удалено: реклама.")
            return

    if any(x in text for x in ['https', 't.me', 'http', 'ftp', 'mailto']):
        if user_status not in ['administrator', 'creator']:
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"Пользователь @{username} был забанен по причине: реклама.")

bot.infinity_polling(none_stop=True)