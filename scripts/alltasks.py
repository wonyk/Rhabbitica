import api

_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"


def alltasks(update, context):
    raw = api.getAll()
    if raw["success"]:
        task = raw["data"]
        update.message.reply_sticker(_reward_sticker)
        update.message.reply_markdown(
            "Here are your tasks as a whole:\n\n"
            "*Todos*:\n - {}\n\n"
            "*Habits*:\n - {}\n\n"
            "*Dailys*:\n - {}\n\n"
            "*Rewards awaiting your claim*:\n - {}".format(
                "\n - ".join([todo["text"] for todo in task["todo"]]),
                "\n - ".join([habit["text"] for habit in task["habit"]]),
                "\n - ".join([daily["text"] for daily in task["daily"]]),
                "\n - ".join([reward["text"] for reward in task["reward"]]),
            )
        )
    elif not raw["success"]:
        update.message.reply_markdown("Please login by using /start.")
    else:
        update.message.reply_markdown("An error occurred. Please try again later.")
