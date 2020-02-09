from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
import logging
import re

TASK_LIST, TASK_OPTIONS, HANDLE_OPTIONS = range(3)

_todo_sticker = "CAADBQADKwADbc38AQcVcPeIfxqcFgQ"
_habit_sticker = "CAADBQADKgADbc38ASR-zdsxRORsFgQ"
_daily_sticker = "CAADBQADKQADbc38AYPOBlWsse41FgQ"
_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"
_all_daily_sticker = "CAADBQADKAADbc38AeLNuuOwBynSFgQ"
_motivation_sticker = "CAADBQADLAADbc38AR9Fg89mOGwIFgQ"
_motivation2_sticker = "CAADBQADLQADbc38Acph7HcoKMhCFgQ"
_level_up_sticker = "CAADBQADMQADbc38AeYQ8SMwNfVWFgQ"
_completed_sticker = "CAADBQADMAADbc38AexYNt85JrF1FgQ"


# Entry point
def view_task(update, context):
    reply_keyboard = [["habits", "todos"], ["rewards", "dailys"]]
    update.message.reply_markdown(
        "What task would you like me to check on?\n"
        "Send /cancel to do something else.\n\n"
        "*Habits* don't have a rigid schedule. You can check them off multiple times per day.\n"
        "*Dailys* repeat on a regular basis. Choose the schedule that works best for you!\n"
        "*To-dos* keep yourself on check!\n"
        "Customise your *rewards*, it's up to you!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TASK_LIST


# Function linked from TASK_LIST
def task_list(update, context):
    taskType = update.message.text
    result = api.get_tasks(taskType)
    # Save the type of task requested and the respective data returned for later use
    context.user_data["viewType"] = taskType

    if result and result["success"] == True and result["data"]:
        context.user_data["taskData"] = result["data"]
        if taskType == "todos":
            update.message.reply_sticker(_todo_sticker)
        elif taskType == "dailys":
            update.message.reply_sticker(_daily_sticker)
        elif taskType == "habits":
            update.message.reply_sticker(_habit_sticker)
        else:
            update.message.reply_sticker(_reward_sticker)
        update.message.reply_markdown(
            "Here are the list of *{}* pending completion:".format(taskType),
            reply_markup=ReplyKeyboardMarkup(
                result["keyboard"], one_time_keyboard=True
            ),
        )
        return TASK_OPTIONS
    elif result["success"] == False:
        update.message.reply_markdown(
            "Please *login* using /start to continue.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_sticker(_motivation_sticker)
        update.message.reply_markdown(
            "Sorry, you do not have any pending *{}*.\n"
            "To create now: /create".format(taskType),
            reply_markup=ReplyKeyboardRemove(),
        )
    return -1


# Function linked from TASK_OPTIONS
def task_options(update, context):
    # update.message.text will come in such a format:
    # '2: Cycle Daily'. The regex will extract the index before the task name.
    array = re.split(": ", update.message.text)
    index = int(array[0]) - 1
    # task_list = api.get_tasks(context.user_data["title"])  # todo / habit etc
    # logging.info(task_list, context.user_data["task"])  # name of task
    # data = _get_id(task_list, context.user_data["title"])
    # context.user_data["task_id"] = data["id"]
    taskType = context.user_data["viewType"]
    data = context.user_data["taskData"][index]
    context.user_data["indivTaskDetails"] = data
    # For todos and dailys
    if taskType == "todos" or taskType == "dailys":
        reply_keyboard = [["Completed", "Cancel"], ["Delete"]]

        update.message.reply_markdown(
            "*Notes*: {}\n\n"
            "What do you want to do with *{}*? \n".format(data["notes"], data["text"]),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    # For rewards
    elif taskType == "rewards":
        reply_keyboard = [["Claim", "Cancel"], ["Delete"]]
        update.message.reply_markdown(
            "*Notes*: {}\n\n"
            "*Gold cost*: {}\n"
            "What do you want to do with *{}*? \n".format(
                data["notes"], data["value"], data["text"]
            ),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
    # For habits
    else:
        habit_reply_keyboard = [["Yes", "Cancel"], ["Delete"]]
        if data["down"]:
            context.user_data["direction"] = "down"
            _votes = data["counterDown"]
        else:
            _votes = data["counterUp"]
            context.user_data["direction"] = "up"
        update.message.reply_markdown(
            "*Notes*: {}\n"
            "*Your habit tracker*: {} times in total\n"
            "Have you done this recently?".format(data["notes"], _votes),
            reply_markup=ReplyKeyboardMarkup(
                habit_reply_keyboard, one_time_keyboard=True
            ),
        )
    return HANDLE_OPTIONS


# Function linked from HANDLE_OPTIONS
def handle_options(update, context):
    option = update.message.text
    taskData = context.user_data["indivTaskDetails"]
    id = taskData["_id"]
    # Completed for todos; Claim for rewards
    if option == "Completed" or option == "Claim":
        result = api.mark_task_done(id, "up")
        return actionSuccess(update, context, result)
    # Only for habits
    elif option == "Yes":
        result = api.mark_task_done(id, context.user_data["direction"])
        return actionSuccess(update, context, result)
    # Universal Delete
    elif option == "Delete":
        result = api.delete_task(id)
        # result will either be True or False
        if result:
            update.message.reply_markdown(
                "*{}* has been successfully deleted.\n\n"
                "To create tasks: /create\n"
                "To view pending tasks: /view".format(taskData["text"]),
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            update.message.reply_text(
                "An error has occurred. Please try again later.",
                reply_markup=ReplyKeyboardRemove(),
            )
        return -1
    # Universal Cancel
    elif option == "Cancel":
        return cancel(update, context)


# Parse results after successfully "Completing" tasks or "Yes" to habits
def actionSuccess(update, context, result):
    taskData = context.user_data["indivTaskDetails"]
    taskType = context.user_data["viewType"]
    if result and result["success"] == True:
        if taskType == "habits":
            update.message.reply_sticker(_level_up_sticker)
        elif taskType == "dailys":
            update.message.reply_sticker(_all_daily_sticker)
        else:
            update.message.reply_sticker(_completed_sticker)
        update.message.reply_markdown(
            "*{}* successfully updated\n\n"
            "Here are your stats:\n*- HP:* {}\n*- Mana Points:* {}\n*- Exp:* {}\n*- Gold:* {}\n*- level:* {}".format(
                taskData["text"],
                round(result["hp"], 1),
                round(result["mp"], 1),
                result["exp"],
                round(result["gp"], 1),
                result["lvl"],
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
    elif result["success"] == False:
        update.message.reply_markdown(
            result["message"], reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_markdown(
            "An *error* occurred while performing the action. Please try again.",
            reply_markup=ReplyKeyboardRemove(),
        )
    return -1

    # if result:
    #     if option == "Claim":
    #         success = result["success"]
    #         if not success:
    #             update.message.reply_text(
    #                 "{}!\nCheck your /stats".format(
    #                     result["message"], reply_markup=ReplyKeyboardRemove()
    #                 )
    #             )
    #         return ConversationHandler.END
    #     if context.user_data["title"] == "daily":
    #         logging.info("Handling user daily's")
    #         update.message.reply_text(
    #             "{} successfully updated\nCheck your /stats".format(
    #                 context.user_data["task"]
    #             )
    #         )
    #         context.bot.send_sticker(
    #             chat_id=update.effective_chat.id, sticker=_all_daily_sticker
    #         )
    #         return ConversationHandler.END
    #     update.message.reply_text(
    #         "{} successfully updated\nCheck your /stats".format(
    #             context.user_data["task"]
    #         )
    #     )
    #     if option == "Yes":
    #         data = result["data"]
    #         update.message.reply_sticker(_level_up_sticker)
    #         update.message.reply_text(
    #             "HP: {}\nExp Level: {}\nLevel: {}\nClass: {}".format(
    #                 data["hp"], data["exp"], data["lvl"], data["class"]
    #             ),
    #             reply_markup=ReplyKeyboardRemove(),
    #         )
    # else:
    #     update.message.reply_text(
    #         "{} Unsuccessfully {}".format(context.user_data["task"], option + "d"),
    #         reply_markup=ReplyKeyboardRemove(),
    #     )
    # return ConversationHandler.END


# def _get_id(tasks, item):
#     for i in tasks:
#         if item != "habit" and item != "reward":
#             return {"id": i[1], "notes": i[2]}
#         elif item == "reward":
#             return {
#                 "id": i[1],
#                 "notes": i[2],
#                 "value": i[3],
#                 "down": i[4],
#                 "counterUp": i[5],
#                 "counterDown": i[6],
#             }
#     return None


# def _create_keyboard(result):
#     output = []
#     for i in result:
#         temp = [i[0]]
#         output.append(temp)
#     return output


def cancel(update, context):
    update.message.reply_text(
        "Bye! Let me know when you want to create a new task.\n"
        "You can always do that using /create.",
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_sticker(_motivation2_sticker)

    return ConversationHandler.END


view_handler = ConversationHandler(
    entry_points=[CommandHandler("view", view_task)],
    states={
        TASK_LIST: [
            MessageHandler(Filters.regex("^(habits|todos|rewards|dailys)$"), task_list)
        ],
        TASK_OPTIONS: [MessageHandler(Filters.text, task_options)],
        HANDLE_OPTIONS: [MessageHandler(Filters.text, handle_options)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True,
)

