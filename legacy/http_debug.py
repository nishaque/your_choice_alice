from app import app
import models as md
from flow import SessionData
from views import get_dialogue

@app.route("/")    
def index():
    return say("Hi")

session_storage = {}

@app.route("/say/<utt>")
def say(utt):
    if "http" not in session_storage:
        session_storage["http"] = SessionData(md.Scenario.query.get(1), *get_dialogue())
    response, buttons = session_storage['http'].iterate(utt)
    links = "\n"
    
    buttons.append("anything")
    for t in buttons:
        links+=f"<a href='/say/{t}'>{t}</a>\n"
    
       
    links+="\n"

    return f"<div><pre>{response}\n{links}\n{session_storage['http'].params}\n{session_storage['http'].guildscores}\n{session_storage['http'].achscores}{session_storage['http'].ach}</pre></div>"


if __name__=="__main__":  
    app.run()
