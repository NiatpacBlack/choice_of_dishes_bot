import os

from dotenv import load_dotenv
from telebot import TeleBot

from services import create_category_keyboard, create_dishes_keyboard, get_all_categories_names, \
    get_dishes_descriptions, create_start_keyboard, create_back_to_categories_button

load_dotenv()
bot = TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет {message.from_user.full_name}, выбери действие:',
                     reply_markup=create_start_keyboard())


@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(callback):
    """Обработка всех полученных callback команд."""

    if callback.data == 'start':
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f'Выбери действие:',
            reply_markup=create_start_keyboard(),
            parse_mode='html'
        )
    elif callback.data == 'menu':
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f'Текущее меню',
            reply_markup=create_category_keyboard(),
            parse_mode='html'
        )
    elif callback.data in get_all_categories_names():
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f'Блюда в категории {callback.data}',
            reply_markup=create_dishes_keyboard(category=callback.data),
            parse_mode='html'
        )
    elif callback not in get_all_categories_names():
        category_name = callback.message.text.split()[-1]

        bot.send_message(
            chat_id=callback.message.chat.id,
            text=get_dishes_descriptions(category=category_name, dish=callback.data),
            reply_markup=create_back_to_categories_button(),
        )

        if __name__ == '__main__':
            bot.polling(non_stop=True, interval=0)
