from flow import Phase
from views import handle
import models as md
from app import db


def test_phase():
    phase1 = Phase("Phase 1").followed_by(
        ["Go to phase 2"], Phase("Phase 2")).followed_by(
        ["Go to phase 3"], Phase("Phase 3").followed_by(
            ["Go to phase 4"], Phase("Phase 4")
        )
    )
    assert phase1.ask() == ("Phase 1", ["Go to phase 2", "Go to phase 3"])
    assert phase1.answer("Gibberish") is phase1
    assert phase1.answer("Go to phase 3").ask() == ("Phase 3", ["Go to phase 4"])
    phase4 = phase1.answer("Go to phase 3").answer("Go to phase 4")
    assert phase4.answer("Go to phase 5") == phase4


def test_views():
    req = {
      "meta": {
        "locale": "ru-RU",
        "timezone": "Europe/Moscow",
        "client_id": "ru.yandex.searchplugin/5.80 (Samsung Galaxy; Android 4.4)",
        "interfaces": {
          "screen": { },
          "account_linking": { }
        }
      },
      "request": {
        "command": "привет",
        "original_utterance": "привет",
        "type": "SimpleUtterance",
      },
      "session": {
        "message_id": 0,
        "session_id": "2eac4854-fce721f3-b845abba-20d60",
        "skill_id": "3ad36498-f5rd-4079-a14b-788652932056",
        "user_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8",
        "user": {
          "user_id": "6C91DA5198D1758C6A9F63A7C5CDDF09359F683B13A18A151FBF4C8B092BB0C2",
          "access_token": "AgAAAAAB4vpbAAApoR1oaCd5yR6eiXSHqOGT8dT"
        },
        "application": {
          "application_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8"
        },
        "new": True
      },
      "version": "1.0"
    }
    res = {
        "version": req['version'],
        "session": req['session'],
        "response": {
            "end_session": False
        }
    }
    handle(req, res)
    assert res["response"]["text"] != ""


def test_models():
    text_data = md.TextData(text="text", tts="tts")
    assert hasattr(text_data, "text")
    assert hasattr(text_data, "tts")
    assert type(text_data.text) is str
