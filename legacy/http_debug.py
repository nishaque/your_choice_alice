"""
Модуль, с помощью которого возможно было тестирование навыка с помощью http запросов в браузере
"""

from app import app
import models as md
from flow import SessionData
from views import get_dialogue


@app.route("/")
def index():
    """
    Начало диалога - заходя в корень сервера мы говорим навыку "Hi"
    """
    return say("Hi")


session_storage = {}


@app.route("/say/<utt>")
def say(utt):
    """
    Обработка полученного в URL высказывания и вывод ответа.
    :param utt: Услышанное навыком
    :return: html с ответом, подсказками и текущим игровым состоянием
    """
    if "http" not in session_storage:
        session_storage["http"] = SessionData(md.Scenario.query.get(1), *get_dialogue())
    response, buttons = session_storage['http'].iterate(utt)
    links = "\n"
    buttons.append("anything")
    for button in buttons:
        links += f"<a href='/say/{button}'>{button}</a>\n"

    links += "\n"

    return (f"<div><pre>{response}\n"
            f"{links}\n"
            f"{session_storage['http'].params}\n"
            f"{session_storage['http'].guildscores}\n"
            f"{session_storage['http'].achscores}"
            f"{session_storage['http'].ach}</pre></div>")


if __name__ == "__main__":
    app.run()
