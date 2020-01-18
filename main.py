import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
import api

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

TASK_NAME, TASK_CREATE = range(2)


def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]

    update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TASK_NAME


def title(update, context):
    user = update.message.from_user
    logger.info("Task to create for %s: %s", user.first_name, update.message.text)
    context.user_data["task"] = update.message.text
    update.message.reply_text(
        "Tell me what you want to name your {}".format(context.user_data["task"])
    )

    return TASK_CREATE


def create_tasks(update, context):
    user = update.message.from_user
    logger.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    _task = context.user_data["task"]
    title = update.message.text
    result = False
    if _task == "todo":
        result = api.create_todo(title)
    elif _task == "habit":
        result = api.create_habit(title)
    elif _task == "daily":
        result = api.create_daily(title)
    elif _task == "reward":
        result = api.create_reward(title)

    if result:
        update.message.reply_text("I have helped you created {}".format(title))
    else:
        update.message.reply_text("error creating {}".format(title))

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("845289799:AAGynfA8Y3WmzK0oTDFMM92z6ADM04pVyIc", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            TASK_NAME: [
                MessageHandler(Filters.regex("^(habit|todo|reward|daily)$"), title)
            ],
            TASK_CREATE: [MessageHandler(Filters.text, create_tasks)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler)

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
