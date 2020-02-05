import requests
import os
import logging

# Dev:
_uid = os.getenv("HABITICA_API_USER")
_key = os.getenv("HABITICA_API_KEY")
_creatorID = os.getenv("HABITICA_API_USER") + "-RabbitHabitica"
_headers = {"x-api-user": _uid, "x-api-key": _key, "x-client": _creatorID}
_auth = {"_uid": _uid, "_key": _key}

# Create a request session for every user
s = requests.Session()


def _url(path):
    return "https://habitica.com/api/v3" + path


def login(name, pw):
    auth = {"username": name, "password": pw}
    try:
        r = s.post(_url("/user/auth/local/login"), data=auth)
        jsonData = r.json()
        if jsonData['success'] == True:
            s.headers.update(
                {
                    "x-api-user": jsonData["data"]["id"],
                    "x-api-key": jsonData["data"]["apiToken"],
                    "x-client": _creatorID,
                }
            )
        return jsonData
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


def get_stats():
    try:
        r = s.get("https://habitica.com/export/userdata.json")
        r.raise_for_status()
        res = r.json()["stats"]
        return res
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


def get_todo():
    resp = get_tasks("todos").json()
    todos = [(i["text"], i["_id"], i["notes"]) for i in resp["data"]]
    return todos


def get_dailys():
    resp = get_tasks("dailys").json()
    dailys = [(i["text"], i["_id"], i["notes"]) for i in resp["data"]]
    return dailys


def get_habits():
    resp = get_tasks("habits").json()
    habits = [
        (
            i["text"],
            i["_id"],
            i["notes"],
            i["up"],
            i["down"],
            i["counterUp"],
            i["counterDown"],
        )
        for i in resp["data"]
    ]
    return habits


def get_rewards():
    resp = get_tasks("rewards").json()
    rewards = [(i["text"], i["_id"], i["notes"], i["value"]) for i in resp["data"]]
    return rewards


def get_tasks(task_type):
    return s.get(_url("/tasks/user"), params={"type": task_type})


# def get_task_id(task_name, task_type):
#     resp = get_tasks(task_type).json()
#     task_id = [i["_id"] for i in resp["data"] if i["text"] == task_name]
#     return task_id


def create_todo(text, message):
    resp = create_task(text, message, "todo", mode="").json()
    print(resp)
    return resp["success"]


def create_daily(text, message):
    return create_task(text, message, "daily", mode="").json()["success"]


def create_habit(text, mode, message, up_enabled=True, down_enabled=True):
    return create_task(text, message, "habit", mode).json()["success"]


def create_reward(text, message):
    return create_task(text, message, "reward", mode="").json()["success"]


def create_task(text, message, task_type, mode):
    if mode != "" and mode == "positive":
        return s.post(
            _url("/tasks/user"),
            data={"text": text, "type": task_type, "down": "false", "notes": message},
        )
    elif mode != "" and mode == "negative":
        return s.post(
            _url("/tasks/user"),
            data={"text": text, "type": task_type, "up": "false", "notes": message},
        )
    return s.post(
        _url("/tasks/user"),
        data={"text": text, "type": task_type, "notes": message, "value": 10},
    )


def mark_task_done(task_id, direction):
    return s.post(_url("/tasks/" + task_id + "/score/" + direction)).json()


def delete_task(task_id):
    resp = s.delete(_url("/tasks/" + task_id))
    return resp.status_code == 200


def mark_checklist(task_id, task_type):
    pass


def update_task(task_id, text, notes, priority):
    return s.post(
        _url("/tasks/" + task_id),
        data={"text": text, "notes": notes, "priority": priority},
    ).json()["success"]
