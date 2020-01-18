import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
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
VIEW_LIST, TASK_OPTIONS, HANDLE_OPTIONS = range(3)


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


def view(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]

    update.message.reply_text(
        "What task would you like to view?\n" "Send /cancel to stop talking to me.\n\n",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TASK_NAME


def _create_keyboard(result):
    output = []
    for i in result:
        temp = [i[0]]
        output.append(temp)
    return output


def _get_task(title):
    result = []
    if title == "todo":
        result = api.get_todo()
        logging.info(result)
    elif title == "habit":
        result = api.get_habits()
    elif title == "daily":
        result = api.get_dailys()
    elif title == "reward":
        result = api.get_rewards()
    return result


def view_list(update, context):
    user = update.message.from_user
    logger.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    context.user_data["title"] = update.message.text
    title = update.message.text
    logging.info(title)
    result = _get_task(title)

    if result:
        reply_keyboard = _create_keyboard(result)
        logging.info(reply_keyboard)
        update.message.reply_text(
            "here is your list of task in {}: \nYou can send the name of the actual task here \n".format(
                title
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    else:
        update.message.reply_text("There is nothing in {}".format(title))

    return TASK_OPTIONS


def _get_id(tasks, item):
    for i in tasks:
        if item == i[0]:
            return i[1]
    return None


def task_options(update, context):
    context.user_data["task"] = update.message.text
    task_list = _get_task(context.user_data["title"])
    logging.info(task_list, context.user_data["task"])
    context.user_data["task_id"] = _get_id(task_list, context.user_data["task"])
    reply_keyboard = [["Completed"], ["Delete"]]

    update.message.reply_text(
        "What do you want to do with {}? \n".format(context.user_data["task"]),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return HANDLE_OPTIONS


def handle_options(update, context):
    option = update.message.text
    result = False
    if option == "Completed":
        logging.info("task id :" + context.user_data["task_id"])
        result = api.mark_task_done(context.user_data["task_id"], "up")
    elif option == "Delete":
        result = api.delete_task(context.user_data["task_id"])

    if result:
        update.message.reply_text(
            "{} successfully {}".format(context.user_data["task"], option)
        )
    else:
        update.message.reply_text(
            "{} Unsuccessfully {}".format(context.user_data["task"], option)
        )

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
    create_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            TASK_NAME: [
                MessageHandler(Filters.regex("^(habit|todo|reward|daily)$"), title)
            ],
            TASK_CREATE: [MessageHandler(Filters.text, create_tasks)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    view_handler = ConversationHandler(
        entry_points=[CommandHandler("view", view)],
        states={
            VIEW_LIST: [
                MessageHandler(Filters.regex("^(habit|todo|reward|daily)$"), view_list)
            ],
            TASK_OPTIONS: [MessageHandler(Filters.text, task_options)],
            HANDLE_OPTIONS: [MessageHandler(Filters.text, handle_options)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

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
