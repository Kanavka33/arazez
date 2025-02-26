import logging
import os
from telebot import TeleBot, types
import random
import sqlite3
bot = TeleBot("8024521533:AAFamZwFm6GAXdMv4aC7GYqrPtgsOfBIETk")

words = []
banned_users = set()
bot.remove_webhook()

conn = sqlite3.connect('words.db', check_same_thread=False)  # Подключение к базе данных
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE
);
''')
conn.commit()

# Загрузка слов из базы данных
cursor.execute('SELECT word FROM words')
words = [row[0] for row in cursor.fetchall()]

@bot.message_handler(commands=['count'])
def count_words(message):
    bot.reply_to(message, f" {len(words)}.")

@bot.message_handler(commands=['clear'])
def clear_words(message):
    if message.from_user.id == 6642397443:
        words.clear()
        bot.reply_to(message, "все чисто.")
    else:
        bot.reply_to(message, "у мужлан нет прав.")

@bot.message_handler(commands=['list'])
def list_words(message):
    if message.from_user.id != 6642397443:
        bot.reply_to(message, "ты не достоин.")
        return

    if not words:
        bot.reply_to(message, "нет слова.")
    else:
        word_list = "\n".join(words)
        bot.reply_to(message, f"\n{word_list}")

@bot.message_handler(commands=['dedik'])
def clear_database(message):
    if message.from_user.id == 6642397443:
        cursor.execute('DELETE FROM words')  # Очистка таблицы
        conn.commit()
        bot.reply_to(message, 'дедик очищен.')
    else:
        bot.reply_to(message, 'У тебя нет прав для выполнения этой операции.')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text.strip():
        try:
            cursor.execute('INSERT INTO words(word) VALUES (?)', (text,))
            conn.commit()
            words.append(text)  # Добавляем слово в список только после успешной записи в БД
        except sqlite3.IntegrityError:
            pass  # Слово уже существует, ничего не делаем

    if len(words) > 0:
        response = random.choice(words)
        bot.send_message(message.chat.id, response)


def send_long_text(bot, chat_id, text):
    """Разбивает длинный текст на части и отправляет их поочередно."""
    MAX_MESSAGE_LENGTH = 2048
    messages_sent = 0

    while len(text) > MAX_MESSAGE_LENGTH and messages_sent < 4:
        bot.send_message(chat_id, text[:MAX_MESSAGE_LENGTH], disable_notification=True)
        text = text[MAX_MESSAGE_LENGTH:]
        messages_sent += 1

    if text:
        bot.send_message(chat_id, text, disable_notification=True)



if __name__ == '__main__':
    try:
        bot.polling()
    finally:
        conn.close()


