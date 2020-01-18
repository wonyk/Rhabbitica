import logging
import json


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

TASK_NAME, TASK_CREATE, TASK_CREATE_HABIT = range(3)
VIEW_LIST, TASK_OPTIONS, HANDLE_OPTIONS = range(3)

def start(update, context):
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker='CAADBQADLwADbc38AdU1wUDmBM3jFgQ')
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to do a few things first?\n\n*Get your userID.*\nTo find your User ID:\n\t\tFor the website: User Icon > Settings > API.\n\t\tFor iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n"
        + "*Get your token Id* \n\t\tTo find your API Token,\nFor the website: User Icon > Settings > API \n\t\tFor iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "*set userID and tokenId after with* /userid _userid here_ *and* /tokenid _tokenid here_ *respectively*",
        parse_mode="Markdown",
    )

def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="To create: /create\n\nTo view: /view"
    )

def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]
    update.message.reply_sticker('CAADBQADLwADbc38AdU1wUDmBM3jFgQ')
    update.message.reply_text(
        "Hi! I am Rhabbit. As your personal assistant, let me help you create a task. "
        "Send /cancel to stop.\n\n"
        "What kind of tasks do you want to create?\n"
        "*Habits* don't have a rigid schedule. You can check them off multiple times per day.\n"
        "*Dailies* repeat on a regular basis. Choose the schedule that works best for you!\n"
        "*To-dos* keep yourself on check!\n"
        "Customise your *rewards*, it's up to you!",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TASK_NAME


def title(update, context):
    user = update.message.from_user
    logger.info("Task to create for %s: %s", user.first_name, update.message.text)
    context.user_data["task"] = update.message.text
    update.message.reply_text(
        "What would you like to name your {}?".format(context.user_data["task"])
    )
    return TASK_CREATE


def create_tasks(update, context):
    user = update.message.from_user
    logger.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    _task = context.user_data["task"]
    title = update.message.text
    context.user_data["title"] = title
    result = False
    if _task == "todo":
        result = api.create_todo(title)
    elif _task == "habit":
        reply_keyboard = [["positive"], ["negative"]]
        update.message.reply_text(
            "What kind of habit is it?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return TASK_CREATE_HABIT
    elif _task == "daily":
        result = api.create_daily(title)
    elif _task == "reward":
        result = api.create_reward(title)

    if result:
        update.message.reply_text("I have helped you create {}".format(title))
        update.message.reply_sticker('CAADBQADMAADbc38AexYNt85JrF1FgQ')
    else:
        update.message.reply_text("error creating {}".format(title))

    return ConversationHandler.END

def create_tasks_habit(update, context):
    user = update.message.from_user
    logger.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    _title = context.user_data["title"]
    mode = update.message.text
    result = False
    result = api.create_habit(_title, mode)
    if result:
        update.message.reply_text("I have helped you create {}".format(_title))
        update.message.reply_sticker('CAADBQADMAADbc38AexYNt85JrF1FgQ')
    else:
        update.message.reply_text("error creating {}".format(title))

    return ConversationHandler.END


def view(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]

    update.message.reply_text(
        "What task would you like me to check on?\n" "Send /cancel to do something else.\n\n",
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
        update.message.reply_sticker('CAADBQADKwADbc38AQcVcPeIfxqcFgQ')
        update.message.reply_text(
            "here is your list of task in {}: \nYou can send the name of the actual task here \n".format(
                title
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    else:
        update.message.reply_sticker('CAADBQADKwADbc38AQcVcPeIfxqcFgQ')
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
            "{} successfully {}".format(context.user_data["task"], option + 'd')
        )
    else:
        update.message.reply_text(
            "{} Unsuccessfully {}".format(context.user_data["task"], option + 'd')
        )

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! Let me know when you want to come back to Rhabbitica.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def stats(update, context)
    update.message.reply_text(self.name = user['profile']['name']
        self.stats = user['stats']
        self.lvl = self.stats['lvl']
        self.xp = self.stats['exp']
        self.gp = self.stats['gp']
        self.hp = self.stats['hp']
        self.mp = self.stats['mp']
        self.xt = self.stats['toNextLevel']
        self.ht = self.stats['maxHealth']
        self.mt = self.stats['maxMP']
        result = api.status()
        )



def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("845289799:AAGynfA8Y3WmzK0oTDFMM92z6ADM04pVyIc", use_context=True)
    # updater = Updater("916014708:AAGdXdRaG-tlpzpiCH05KVk0oO26T6fGVNc", use_context=True)

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
            TASK_CREATE_HABIT: [MessageHandler(Filters.text, create_tasks_habit)],
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

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

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
