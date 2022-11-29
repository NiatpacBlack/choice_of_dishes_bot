import os

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()
bot = TeleBot(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
    pass
