from app import app
import json
from flask import request, redirect, url_for
from flow import Phase, SessionData
import models as md

def _(td):
    if hasattr(td, "text"):
        return td.text
    else:
        return td

def get_dialogue():
    dial = dict(map(lambda e:(e.tag,e.td), md.Dialogue.query.all()))
    utter_query =  md.DialUtter.query.all()
    exp_utter = dict()
    for u in utter_query:
        if u.tag in exp_utter:
            exp_utter[u.tag].append(u.text)
        else:
            exp_utter[u.tag] = list()
            exp_utter[u.tag].append(u.text)
    return dial, exp_utter

session_storage = {}

@app.route("/json", methods=['POST'])
def r_index():
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
    user_id = req["session"]["user_id"]
    if req["session"]["new"]:
        session_storage[user_id] = SessionData(md.Scenario.query.get(1), *get_dialogue())
    if (session_storage[user_id].end_session):
        res["response"]["end_session"] = True    
    text, btns  = session_storage[user_id].iterate(req["request"]["command"])
    btns = [dict(title=b) for b in btns]
    res["response"]["text"], res["response"]["buttons"] = text, btns

