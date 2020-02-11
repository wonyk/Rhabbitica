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

def error(update, context):
    logging.warning('Update "%s" caused error "%s"', update, context.error)


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
