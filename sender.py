import logging
import os
import random

from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# getting consts
load_dotenv()
TOKEN = os.getenv('TG_TOKEN')
phrases = open('phrases.txt', 'rt', encoding='utf-8').readlines()
PHRASE_BASE = [phrases[k] for k in range(len(phrases)-1)]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'дарова! вошел в хату - представься. Читать я не умею, поэтому покажи мне фото'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Сюда можно отправлять только фото')


def echo(update: Update, context: CallbackContext) -> None:
    # скачиваем фото на рабочую машину
    photo_from_message = update.message.photo[-1].get_file()
    photo_from_message.download('photo_file.jpg')

    # открываем фотку и добавляем на неё фразу
    phrase = PHRASE_BASE[random.randint(0, 4)]
    photo = Image.open('photo_file.jpg')
    width, height = photo.size
    caption = ImageDraw.Draw(photo)

    # далее идут танцы с бубном, которые надо исправить
    font = ImageFont.truetype('Lobster.ttf', size=round(height * 0.1))
    text_w, text_h = caption.textsize(phrase, font)
    proportion = text_h/text_w
    font = ImageFont.truetype(
        'Lobster.ttf',
        size=min(round(height * 0.2), round(width * 0.64 * proportion))
    )
    text_w, text_h = caption.textsize(phrase, font)
    start_position = (round((width - text_w)/2), round((height - text_h)*0.9))
    caption.text(start_position, phrase, font=font, fill='#FFFFFF')
    photo.save('rdy_to_send.jpg')

    # отправляем фото пользователю обратно
    update.message.reply_photo(photo=open('rdy_to_send.jpg', 'rb'))

    # удаляем следы нашей работы
    os.remove('rdy_to_send.jpg')
    os.remove('photo_file.jpg')


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
