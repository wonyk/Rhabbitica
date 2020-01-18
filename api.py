import requests


_uid = "43a51e03-bf00-4832-a47e-411ec309466f"
_tid = "ff4bc2bc-a9d8-4e87-831e-e6b886466bec"
_headers = {
    "x-api-user": _uid,
    "x-api-key": _tid,
}


def _url(path):
    return "https://habitica.com/api/v3" + path


def set_id(uid, tid):
    _uid = uid
    _tid = tid


def get_tasks():
    return requests.get(_url("/tasks/user"), params={"type": ""}, headers=_headers,)


def describe_task(task_id):
    return requests.get(_url("/tasks/{:d}/".format(task_id)))


def create_task(text, task_type):
    return requests.post(
        _url("/tasks/user"), headers=_headers, data={"text": text, "type": task_type,},
    )


def task_done(task_id):
    return requests.delete(_url("/tasks/{:d}/".format(task_id)))


def update_task(task_id, summary, description):
    url = _url("/tasks/{:d}/".format(task_id))
    return requests.put(url, json={"summary": summary, "description": description,})
