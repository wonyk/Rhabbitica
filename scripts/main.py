import logging
import json
import os

# Import script files
import api
from start import start_handler
from help import help
from stats import stats
from alltasks import alltasks
from create import create_handler
from view import view_handler

# Uses .env files to load sensitive information
from dotenv import load_dotenv

load_dotenv()

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

# import schedule
# import time
# import threading
# import re
# import random

# class ScheduleThread(threading.Thread):
#     def __init__(self, *pargs, **kwargs):
#         super().__init__(*pargs, daemon=True, name="scheduler", **kwargs)

#     def run(self):
#         while True:
#             schedule.run_pending()
#             time.sleep(schedule.idle_seconds())


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# declare constants
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
_completed_sticker = "CAADBQADMAADbc38AexYNt85JrF1FgQ"
_todo_sticker = "CAADBQADKwADbc38AQcVcPeIfxqcFgQ"
_habit_sticker = "CAADBQADKgADbc38ASR-zdsxRORsFgQ"
_daily_sticker = "CAADBQADKQADbc38AYPOBlWsse41FgQ"
_all_daily_sticker = "CAADBQADKAADbc38AeLNuuOwBynSFgQ"
_motivation_sticker = "CAADBQADLAADbc38AR9Fg89mOGwIFgQ"
_motivation2_sticker = "CAADBQADLQADbc38Acph7HcoKMhCFgQ"
_motivation3_sticker = "CAADBQADLgADbc38AWvtjZz2orqBFgQ"
_motivation_stickers = [_motivation_sticker, _motivation2_sticker, _motivation3_sticker]
_level_up_sticker = "CAADBQADMQADbc38AeYQ8SMwNfVWFgQ"
_coin_sticker = "CAADBQADMgADbc38AWOrA-yiyuDxFgQ"
_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"
_quotes = [
    "If you want to achieve greatness stop asking for permission. --Anonymous",
    "Things work out best for those who make the best of how things work out. --John Wooden",
    "To live a creative life, we must lose our fear of being wrong. --Anonymous",
    "If you are not willing to risk the usual you will have to settle for the ordinary. --Jim Rohn",
    "Trust because you are willing to accept the risk, not because it's safe or certain. --Anonymous",
    "Take up one idea. Make that one idea your life--think of it, dream of it, live on that idea. Let the brain, muscles, nerves, every part of your body, be full of that idea, and just leave every other idea alone. This is the way to success. --Swami Vivekananda",
    "All our dreams can come true if we have the courage to pursue them. --Walt Disney",
    "Good things come to people who wait, but better things come to those who go out and get them. --Anonymous",
    "If you do what you always did, you will get what you always got. --Anonymous",
    "Success is walking from failure to failure with no loss of enthusiasm. --Winston Churchill",
    "Just when the caterpillar thought the world was ending, he turned into a butterfly. --Proverb",
    "Successful entrepreneurs are givers and not takers of positive energy. --Anonymous",
    "Whenever you see a successful person you only see the public glories, never the private sacrifices to reach them.  --Vaibhav Shah",
    "Opportunities don't happen, you create them. --Chris Grosser",
    "Try not to become a person of success, but rather try to become a person of value. --Albert Einstein",
    "Great minds discuss ideas; average minds discuss events; small minds discuss people. --Eleanor Roosevelt",
    "I have not failed. I've just found 10,000 ways that won't work. --Thomas A. Edison",
    "If you don't value your time, neither will others. Stop giving away your time and talents--start charging for it. --Kim Garst",
    "A successful man is one who can lay a firm foundation with the bricks others have thrown at him.--David Brinkley",
    "No one can make you feel inferior without your consent. --Eleanor Roosevelt",
]

# _quote_time = 100
# _quote_pic_time = 150

# def quote_gen(update, context):
#     quote = random.choice(_quotes)
#     context.bot.send_message(
#         chat_id=update.message.chat.id, text="{}".format(quote),
#     )


# def quote_pic_gen(update, context):
#     sticker = random.choice(_motivation_stickers)
#     logging.info(sticker)
#     context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=sticker)

def error(update, context):
    logging.warning('Update "%s" caused error "%s"', update, context.error)


# def scheduleHandler(update, context):
#     query = update.callback_query
#     completed = re.search("^1", query.data)
#     if completed != None:
#         query.edit_message_text(text="Completed")
#         api.mark_task_done(query.data[1:], "up")
#         api.mark_task_done(query.data[1:], "down")
#     else:
#         query.edit_message_text(text="Did not complete")


def main():
    updater = Updater(os.getenv("TELEGRAM_API_KEY"), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler for creating and viewing
    dp.add_handler(start_handler)
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("alltasks", alltasks))
    dp.add_handler(create_handler)
    dp.add_handler(view_handler)
    # dp.add_handler(CallbackQueryHandler(scheduleHandler))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
