import telebot
import sqlite3
import validators
import random

bot = telebot.TeleBot("7722802971:AAH5EZ1SDxBVP5X2uv3wFDnR7FexhvAUxa8")


def is_empty_db(user_id, link):
    connect = sqlite3.connect("links.db")
    cursor = connect.cursor()
    cursor.execute(
        "SELECT id FROM links WHERE user_id = ? AND link = ?", (user_id, link)
    )
    row = cursor.fetchone()
    connect.close()

    if row is None:
        return False

    return True


def add_link_to_db(user_id, link):
    connect = sqlite3.connect("links.db")
    cursor = connect.cursor()
    cursor.execute("INSERT INTO links (user_id, link) VALUES (?, ?)", (user_id, link))
    connect.commit()
    connect.close()


def get_link_from_db(user_id):
    connect = sqlite3.connect("links.db")
    cursor = connect.cursor()
    cursor.execute("SELECT id, link FROM links WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()

    if rows:
        random_link = random.choice(rows)
        link_id, link_url = random_link
        cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
        connect.commit()
        connect.close()
        return link_url

    connect.close()
    return None


msg = """Привет! Я бот, который поможет не забыть прочитать статьи, найденные тобою в интернете :)
\n - Чтобы я запомнил статью, достаточно передать мне ссылку на неё. К примеру https://example.com.
\n - Чтобы получить случайную статью, достаточно передать мне команду /get_article.
\n Но помни! Отдавая статью тебе на прочтение, я больше не храню её в моей базе. Так что тебе точно нужно её изучить."""


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, msg)


@bot.message_handler(commands=["get_article"])
def get_article(message):
    user_id = message.from_user.id
    random_link = get_link_from_db(user_id)
    if random_link:
        bot.reply_to(
            message, f"Вы хотели прочитать: {random_link} Самое время это сделать!"
        )
    else:
        bot.reply_to(
            message,
            "Пока что вы не сохранили ни одной ссылки :(. Если нашли что-то стоящее, я жду!",
        )


@bot.message_handler(content_types=["text"])
def handle_message(message):
    user_id = message.from_user.id
    user_message = message.text

    if validators.url(user_message):
        if is_empty_db(user_id, user_message):
            bot.reply_to(message, "Упс, вы уже это сохраняли :)")
        else:
            add_link_to_db(user_id, user_message)
            bot.reply_to(message, "Сохранил, спасибо!")
    else:
        bot.reply_to(message, "Некорректная ссылка на сайт")


if __name__ == "__main__":
    connect = sqlite3.connect("links.db")
    cursor = connect.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                link TEXT NOT NULL
        )"""
    )
    connect.commit()
    connect.close()
    bot.polling(none_stop=True)
