import logging
import json


conf = {
    "url": "https://habitica.com",
    "login": "43a51e03-bf00-4832-a47e-411ec309466f",
    "password": "ff4bc2bc-a9d8-4e87-831e-e6b886466bec",
}
# api = Habitipy(conf)
# print(api.user.get())

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
import api
import schedule
import time
import threading
import re
import random


class ScheduleThread(threading.Thread):
    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, daemon=True, name="scheduler", **kwargs)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(schedule.idle_seconds())


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# constants
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
_level_up_sticker = 'CAADBQADMQADbc38AeYQ8SMwNfVWFgQ'
_coin_sticker = 'CAADBQADMgADbc38AWOrA-yiyuDxFgQ'
_reward_sticker = 'CAADBQADMwADbc38Ab8X1fBrA7qZFgQ'
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

TASK_NAME, TASK_CREATE, TASK_CREATE_HABIT = range(3)
VIEW_LIST, TASK_OPTIONS, HANDLE_OPTIONS = range(3)


def quote_gen(update, context):
    sticker = random.choice(_motivation_stickers)
    logging.info(sticker)
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=sticker)
    quote = random.choice(_quotes)
    context.bot.send_message(
        chat_id=update.message.chat.id, text="{}".format(quote),
    )


def start(update, context):
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=_start_sticker)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to identify yourself?\n\n*Get your userID.*\nTo find your User ID:\n\t\tFrom the website: User Icon > Settings > API.\n\t\tFrom iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n"
        + "*Get your token Id* \n\t\tTo find your API Token,\nFrom the website: User Icon > Settings > API \n\t\tFrom iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "*set userID and tokenId after with* /userid _userid here_ *and* /tokenid _tokenid here_ *respectively*",
        parse_mode="Markdown",
    )
    schedule.every(10).seconds.do(quote_gen, update, context)
    ScheduleThread().start()


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="To create: /create\n\nTo view: /view"
    )


def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]
    update.message.reply_sticker(_start_sticker)
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
    if update.message.text == "todo":
        update.message.reply_sticker(_todo_sticker)
    elif update.message.text == "daily":
        update.message.reply_sticker(_daily_sticker)
    elif update.message.text == "habit":
        update.message.reply_sticker(_habit_sticker)
    else:
        update.message.reply_sticker(_reward_sticker)
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
    others = {}
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
        update.message.reply_sticker(_completed_sticker)
        others = _create_keyboard(_get_task(_task))
        update.message.reply_text(
            "Do not forget about these:\n - {}".format(
                "\n - ".join([str(i[0]) for i in others])
            )
        )
    else:
        update.message.reply_text("error creating {}".format(title))

    return ConversationHandler.END


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def remind_habits(update, context):
    task_list = _get_task("habit")
    for task in task_list:
        # Show the task with the option to mark the item as done // not done.
        keyboard = [
            InlineKeyboardButton("Did it", callback_data="1" + task[1]),
            InlineKeyboardButton("Didn't do it", callback_data="2"+task[1]),
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=1))
        logging.info("Printing: " + task[0])
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Did you {}".format(task[0]),
            reply_markup=reply_markup,
        )


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
        update.message.reply_sticker(_completed_sticker)
        others = _create_keyboard(_get_task('habit'))
        update.message.reply_text("Do not forget about these:\n - {}".format("\n - ".join([str(i[0]) for i in others])))
        schedule.every(20).seconds.do(remind_habits, update, context)
        ScheduleThread().start()
    else:
        update.message.reply_text("error creating {}".format(title))

    return ConversationHandler.END


def view(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]

    update.message.reply_text(
        "What task would you like me to check on?\n"
        "Send /cancel to do something else.\n\n",
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
        if title == "todo":
            update.message.reply_sticker(_todo_sticker)
        elif title == "daily":
            update.message.reply_sticker(_daily_sticker)
        elif title == "habit":
            update.message.reply_sticker(_habit_sticker)
        else:
            update.message.reply_sticker(_reward_sticker)
        update.message.reply_text(
            "Here is your list of tasks in {}: \nYou can send the name of the actual task here \n".format(
                title
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    else:
        update.message.reply_sticker(_motivation_sticker)
        update.message.reply_text("There is nothing in {}".format(title))

    return TASK_OPTIONS


def _get_id(tasks, item):
    for i in tasks:
        if item != "habit" and item != 'reward':
            return {"id": i[1], "notes": i[2]}
        elif item == 'reward':
            return {
                "id": i[1],
                "notes": i[2],
                "value": i[3]
            }
        else:
            return {
                "id": i[1],
                "notes": i[2],
                "up": i[3],
                "down": i[4],
                "counterUp": i[5],
                "counterDown": i[6],
            }
    return None


def task_options(update, context):
    context.user_data["task"] = update.message.text
    task_list = _get_task(context.user_data["title"]) #todo / habit etc
    logging.info(task_list, context.user_data["task"]) #name of task
    data = _get_id(task_list, context.user_data["title"])
    context.user_data["task_id"] = data["id"]
    if context.user_data["title"] != 'habit' and context.user_data["title"] != 'reward':
        reply_keyboard = [["Completed", "Cancel"], ["Delete"]]

        update.message.reply_text(
            "Notes: {}\n\n"
            "What do you want to do with {}? \n".format(
                data["notes"], context.user_data["task"]
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    elif context.user_data["title"] == 'reward':
        reply_keyboard = [["Claim", "Cancel"], ["Delete"]]
        update.message.reply_text(
            "Notes: {}\n\n"
            "Gold cost: {}\n"
            "What do you want to do with {}? \n".format(
                data["notes"], data['value'], context.user_data["task"]
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    else:
        habit_reply_keyboard = [["Yes", "Cancel"], ["Delete"]]
        context.user_data["_positive"] = "up"
        _votes = data["counterUp"]
        if data["down"] == True:
            context.user_data["_positive"] = "down"
            _votes = data["counterDown"]
        update.message.reply_text(
            "Notes: {}\n"
            "Your habit tracker: {} times\n"
            "Have you done this recently? \n".format(data["notes"], _votes),
            reply_markup=ReplyKeyboardMarkup(
                habit_reply_keyboard, one_time_keyboard=True
            ),
        )
    return HANDLE_OPTIONS


def handle_options(update, context):
    option = update.message.text
    result = False
    if option == "Completed" or option == 'Claim':
        logging.info("task id :" + context.user_data["task_id"])
        result = api.mark_task_done(context.user_data["task_id"], "up")
    elif option == "Delete":
        result = api.delete_task(context.user_data["task_id"])
    elif option == "Yes":
        print(context.user_data["_positive"])
        result = api.mark_task_done(context.user_data["task_id"], context.user_data["_positive"])
    elif option == 'Cancel':
        return cancel(update, context)
    if result:
        if (option == 'Claim'):
            success = result["success"]
            if not success:
                update.message.reply_text("{}!\nCheck your /stats".format(result["message"], reply_markup=ReplyKeyboardRemove()))
            return ConversationHandler.END

        update.message.reply_text(
            "{} successfully updated\nCheck your /stats".format(context.user_data["task"])
        )
        if (option == 'Yes'):
            data = result["data"]
            update.message.reply_sticker(_level_up_sticker)
            update.message.reply_text(
            "HP: {}\nExp Level: {}\nLevel: {}\nClass: {}".format(data['hp'], data['exp'], data['lvl'], data['class']),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text(
            "{} Unsuccessfully {}".format(context.user_data["task"], option + "d"),
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! Let me know when you want to come back to Rhabbitica.",
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_sticker(_motivation2_sticker)

    return ConversationHandler.END


def stats(update, context):
    status = api.get_status()
    logging.info(status)
    update.message.reply_sticker(_coin_sticker)
    update.message.reply_markdown(
        "Here are your stats: \n"
        + "- HP: {} \n".format(status["hp"])
        + "- Mana Points: {} \n".format(round(status["mp"], 1))
        + "- Exp: {}\n".format(status["exp"])
        + "- Gold: {}\n".format(round(status["gp"], 1))
        + "- level: {}\n".format(status["lvl"]),
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def scheduleHandler(update, context):
    query = update.callback_query
    logging.info(query.data)
    if (re.search("^1", query.data) != 'None'):
        query.edit_message_text(text="Completed")
        api.mark_task_done(query.data[1:], 'up')
        api.mark_task_done(query.data[1:], 'down')
    else:
        query.edit_message_text(text="Did not complete")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # updater = Updater("845289799:AAGynfA8Y3WmzK0oTDFMM92z6ADM04pVyIc", use_context=True)
    updater = Updater("916014708:AAGdXdRaG-tlpzpiCH05KVk0oO26T6fGVNc", use_context=True)

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
    dp.add_handler(CommandHandler("stats", stats))

    dp.add_handler(create_handler)
    dp.add_handler(view_handler)
    dp.add_handler(CallbackQueryHandler(scheduleHandler))
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
