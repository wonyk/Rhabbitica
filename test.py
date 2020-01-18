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


def start(update, context):
    context.bot.send_sticker(
        chat_id=update.effective_chat.id, sticker="CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi! please do a few things first.\n\n*Get your userID.*\nTo find your User ID:\n\t\tFor the website: User Icon > Settings > API.\n\t\tFor iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n"
        + "*Get your token Id* \n\t\tTo find your API Token,\nFor the website: User Icon > Settings > API \n\t\tFor iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "*set userID and tokenId after with* /userid _userid here_ *and* /tokenid _tokenid here_ *respectively*",
        parse_mode="Markdown",
    )


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="To create: /create\n\nTo view: /view"
    )


def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]
    update.message.reply_sticker("CAADBQADLwADbc38AdU1wUDmBM3jFgQ")
    update.message.reply_text(
        "Hi! I am Rhabbitica. I will help you through the creation process. "
        "Send /cancel to stop.\n\n"
        "What kind of tasks do you want to create?\n"
        "*Habits* don't have a rigid schedule. You can check them off multiple times per day.\n"
        "Dailies repeat on a regular basis. Choose the schedule that works best for you!\n"
        "Todos keep yourself on check!\n"
        "Customise your rewards, it's up to you!",
        parse_mode="Markdown",
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
        update.message.reply_sticker("CAADBQADMAADbc38AexYNt85JrF1FgQ")
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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
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
