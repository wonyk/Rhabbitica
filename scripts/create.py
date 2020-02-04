from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
import logging

TASK_NAME, TASK_MESSAGE, TASK_CREATE, TASK_CREATE_HABIT = range(4)
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
_completed_sticker = "CAADBQADMAADbc38AexYNt85JrF1FgQ"
_todo_sticker = "CAADBQADKwADbc38AQcVcPeIfxqcFgQ"
_habit_sticker = "CAADBQADKgADbc38ASR-zdsxRORsFgQ"
_daily_sticker = "CAADBQADKQADbc38AYPOBlWsse41FgQ"
_motivation2_sticker = "CAADBQADLQADbc38Acph7HcoKMhCFgQ"


def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]
    update.message.reply_sticker(_start_sticker)
    update.message.reply_markdown(
        "Hi! I am Rhabbit, your personal assistant, great to see you again!"
        "\nLet me help you create a new task."
        "\nTo cancel: /cancel"
        "\nTo restart: /create\n\n"
        "What kind of tasks do you want to create?\n"
        "*Habits* don't have a rigid schedule. You can check them off multiple times per day.\n"
        "*Dailies* repeat on a regular basis. Choose the schedule that works best for you!\n"
        "*To-dos* keep yourself on check!\n"
        "Customise your *rewards*, it's up to you!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TASK_NAME


# Function linked from TASK_NAME
def taskName(update, context):
    user = update.message.from_user
    logging.info("Task to create for %s: %s", user.first_name, update.message.text)
    context.user_data["task"] = update.message.text
    if update.message.text == "todo":
        update.message.reply_sticker(_todo_sticker)
    elif update.message.text == "daily":
        update.message.reply_sticker(_daily_sticker)
    elif update.message.text == "habit":
        update.message.reply_sticker(_habit_sticker)
    return TASK_MESSAGE


# Function linked from TASK_MESSAGE
def taskMessage(update, context):
    user = update.message.from_user
    logging.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    _task = context.user_data["task"]  # habit / todo etc
    title = update.message.text
    context.user_data["title"] = title  # title of the task (name)
    update.message.reply_text("Please key in details for {}?".format(title))
    return TASK_CREATE


# Function linked from TASK_CREATE
def create_tasks(update, context):
    user = update.message.from_user
    logging.info(
        "Message of task to create for %s: %s", user.first_name, update.message.text
    )
    message = update.message.text
    context.user_data["message"] = message
    result = False
    others = {}
    _task = context.user_data["task"]
    title = context.user_data["title"]
    if _task == "todo":
        result = api.create_todo(title, message)
    elif _task == "habit":
        reply_keyboard = [["positive", "negative"]]
        update.message.reply_text(
            "What kind of habit is it?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return TASK_CREATE_HABIT
    elif _task == "daily":
        result = api.create_daily(title, message)
    elif _task == "reward":
        result = api.create_reward(title, message)

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
            InlineKeyboardButton("Didn't do it", callback_data="2" + task[1]),
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=1))
        logging.info("Printing: " + task[0])
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Did you {}".format(task[0]),
            reply_markup=reply_markup,
        )


# Function linked from TASK_CREATE_HABIT
def create_tasks_habit(update, context):
    user = update.message.from_user
    logging.info(
        "Name of task to create for %s: %s", user.first_name, update.message.text
    )
    _title = context.user_data["title"]
    mode = update.message.text
    message = context.user_data["message"]
    result = False
    result = api.create_habit(_title, mode, message)
    if result:
        update.message.reply_text("I have helped you create {}".format(_title))
        update.message.reply_sticker(_completed_sticker)
        others = _create_keyboard(_get_task("habit"))
        update.message.reply_text(
            "Do not forget about these:\n - {}".format(
                "\n - ".join([str(i[0]) for i in others])
            )
        )
        # schedule.every(120).seconds.do(remind_habits, update, context)
        # ScheduleThread().start()
    else:
        update.message.reply_text("error creating {}".format(_title))

    return ConversationHandler.END


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


def cancel(update, context):
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! Let me know when you want to come back to Rhabbitica.",
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_sticker(_motivation2_sticker)

    return ConversationHandler.END


create_handler = ConversationHandler(
    entry_points=[CommandHandler("create", create)],
    states={
        TASK_NAME: [
            MessageHandler(Filters.regex("^(habit|todo|reward|daily)$"), taskName)
        ],
        TASK_MESSAGE: [MessageHandler(Filters.text, taskMessage)],
        TASK_CREATE: [MessageHandler(Filters.text, create_tasks)],
        TASK_CREATE_HABIT: [MessageHandler(Filters.text, create_tasks_habit)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True,
)

