from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
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
_reward_sticker = "CAADBQADLAADbc38AR9Fg89mOGwIFgQ"
_motivation2_sticker = "CAADBQADLQADbc38Acph7HcoKMhCFgQ"

# Called when /create is matched
def create(update, context):
    reply_keyboard = [["habit", "todo"], ["reward", "daily"]]
    update.message.reply_sticker(_start_sticker)
    update.message.reply_markdown(
        "Hi! I am Rhabbit, your personal assistant, great to see you again!"
        "\nLet me help you create a new task."
        "\nTo cancel: /cancel\n\n"
        "What kind of tasks do you want to create?\n"
        "*Habits* don't have a rigid schedule. You can check them off multiple times per day.\n"
        "*Dailys* repeat on a regular basis. Choose the schedule that works best for you!\n"
        "*To-dos* keep yourself on check!\n"
        "Customise your *rewards*, it's up to you!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return TASK_NAME


# Function linked from TASK_NAME
def taskName(update, context):
    context.user_data["taskType"] = update.message.text
    if update.message.text == "todo":
        update.message.reply_sticker(_todo_sticker)
    elif update.message.text == "daily":
        update.message.reply_sticker(_daily_sticker)
    elif update.message.text == "habit":
        update.message.reply_sticker(_habit_sticker)
    else:
        update.message.reply_sticker(_reward_sticker)
    update.message.reply_markdown(
        "Please key in your preferred name for *{}*:".format(update.message.text),
        reply_markup=ReplyKeyboardRemove(),
    )
    return TASK_MESSAGE


# Function linked from TASK_MESSAGE
def taskMessage(update, context):
    title = update.message.text
    context.user_data["title"] = title
    update.message.reply_markdown("Please key in details for *{}*:".format(title))
    return TASK_CREATE


# Function linked from TASK_CREATE
def create_tasks(update, context):
    task = context.user_data["taskType"]
    description = update.message.text
    context.user_data["description"] = description
    # Redirect to another state specially for Habits
    if task == "habit":
        reply_keyboard = [["positive", "negative"]]
        update.message.reply_text(
            "What kind of habit is it?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return TASK_CREATE_HABIT
    else:
        title = context.user_data["title"]
        result = api.create_task(title, task, description)
    # Process the results:
    if result and result["success"] == True:
        create_success(update, result)
    elif result["success"] == False:
        update.message.reply_markdown(
            "Please *login* using /start to continue.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_markdown("*Error* creating {}".format(task))

    return ConversationHandler.END


# Function linked from TASK_CREATE_HABIT
def create_tasks_habit(update, context):
    # title - Task name
    # description - Task description / detail
    # direction - Unique for Habits (Positive / Negative)
    title = context.user_data["title"]
    description = context.user_data["description"]
    direction = update.message.text
    if direction == "positive":
        result = api.create_task(title, "habit", description, "up")
    else:
        result = api.create_task(title, "habit", description, "down")
    # Process results:
    if result and result["success"] == True:
        create_success(update, result)
    elif result["success"] == False:
        update.message.reply_markdown(
            "Please *login* using /start to continue.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_markdown(
            "*Error* creating habit", reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def create_success(update, result):
    data = result["data"]
    update.message.reply_sticker(_completed_sticker)
    update.message.reply_markdown(
        "I have helped you create a new {}!\n\n"
        "*Here are the details:*\n"
        "Name: {}\n"
        "Notes: {}".format(data["type"], data["text"], data["notes"])
    )
    otherTasks = api.get_tasks(data["type"] + "s")
    update.message.reply_markdown(
        "*Here are all your tasks, please do not forget about them*:\n{}".format(
            "\n".join([str(i[0]) for i in otherTasks["keyboard"]])
        ),
        reply_markup=ReplyKeyboardRemove(),
    )


def cancel(update, context):
    update.message.reply_text(
        "Bye! Let me know when you want to create a new task.\n"
        "You can always do that using /create.",
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

