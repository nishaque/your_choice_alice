"""
Модуль, в котором описывается обработка запроса.
"""

import json
from flask import request
from app import app
from flow import SessionData
import models as md


def get_dialogue():
    """
    Загружает из таблиц Dialogue и DialUtter строки.
    :return: (dict с содержимым таблицы Dialogue: { "tag" : td, ... },
              dict с содержимым таблицы DialUtter: { "tag" : [ text, ... ], ... })
    """
    dial = dict(map(lambda e: (e.tag, e.td), md.Dialogue.query.all()))
    utter_query = md.DialUtter.query.all()
    exp_utter = dict()
    for utter in utter_query:
        if utter.tag not in exp_utter:
            exp_utter[utter.tag] = list()
        exp_utter[utter.tag].append(utter.text)
    return dial, exp_utter


session_storage = {}


@app.route("/json", methods=['POST'])
def skill():
    """
    Основной маршрут приложения, вызывающий хендлер handle.
    :return: JSON-string
    """
    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle(request.json, response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def handle(req, res):
    """
    Хендлер, создающий новую игровую сессию для новых пользователей или
    обрабатывающий сказанное пользователем и делающий игровой шаг для уже идущей игры,
    и выдающий ответ.
    :param req: JSON запрос (dict)
    :param res: JSON ответ (dict)
    :return:
    """
    user_id = req["session"]["user_id"]
    if req["session"]["new"]:
        session_storage[user_id] = SessionData(md.Scenario.query.get(1), *get_dialogue())
    if session_storage[user_id].end_session:
        res["response"]["end_session"] = True
    text, buttons = session_storage[user_id].iterate(req["request"]["command"])
    buttons = [dict(title=button) for button in buttons]
    res["response"]["text"], res["response"]["buttons"] = text, buttons
