import logging
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

from telegram.ext import (
    Updater,
    CommandHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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
