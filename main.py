import os
import requests
from datetime import datetime

USERS_URL = 'https://json.medrocket.ru/users'
TASKS_URL = 'https://json.medrocket.ru/todos'


def upload_tasks(user):
    params = {'userId': user['id']}
    response = requests.get(TASKS_URL, params=params).json()
    return response


def upload_users():
    response = requests.get(USERS_URL).json()
    return response


def generate_report(user):
    tasks = upload_tasks(user)

    completed = []
    pending = []

    for task in tasks:
        if task['completed']:
            completed.append(task)
        else:
            pending.append(task)

    company = user['company']['name']
    name = f"{user['name']} <{user['email']}>"

    now = datetime.now().strftime('%d.%m.%Y %H:%M')

    lines = [
        f"# Отчёт для {company}.",
        f"{name} {now}\n"
        f"Всего задач: {len(tasks)}",
        "",
        f"## Актуальные задачи ({len(pending)}):",
    ]

    for task in pending:
        title = task['title'][:46] + '…' if len(task['title']) > 46 else task['title']
        lines.append(f"- {title}")

    lines += [
        "",
        f"## Завершённые задачи ({len(completed)}):",
    ]

    for task in completed:
        title = task['title'][:46] + '…' if len(task['title']) > 46 else task['title']
        lines.append(f"- {title}")

    return "\n".join(lines)


def write_report(user, report):
    filename = f"{user['username']}.txt"

    if os.path.exists(filename):
        stat = os.stat(filename)
        date_created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%dT%H_%M_%S')

        new_name = f"old_{user['username']}_{date_created}.txt"
        try:
            os.rename(filename, new_name)
        except FileExistsError:
            new_name = f"old_{user['username']}_{date_created}.txt"
            os.rename(filename, new_name)

    with open(filename, 'x', encoding='utf-8') as f:
        f.write(report)


def main():
    users = upload_users()

    if not os.path.exists('tasks'):
        os.mkdir('tasks')

    os.chdir('tasks')

    for user in users:
        report = generate_report(user)
        write_report(user, report)


if __name__ == '__main__':
    main()
