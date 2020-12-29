
def get_followed_by_end(p, text, ses_dat):
    p.dialogue += text
    p.justpass = True
    p.next = []
    p.onspoke = None
    def die(nu, sd):
        sd.end_session = True
    p.followed_by([], Phase(_(ses_dat.dial["goodbye"]),ses_dat,onspoke=die))

def predetermine(p, o, ses_dat):
    ses_dat.move_count+=1
    for e in o.guild_effects:
        ses_dat.guildscores[e.guild_id] +=e.strength
    for e in o.param_effects:
        ses_dat.params[e.param_id] +=e.strength
    for e in o.ach_effects:
        ses_dat.achscores[e.ach_id] +=e.strength

    for param in ses_dat.sc.params:
        for w in param.weights:
            ses_dat.guildscores[w.guild_id] += ses_dat.params[w.param_id] * w.func_param


    for a in ses_dat.sc.achievements:
        if(a not in ses_dat.ach) and \
            (ses_dat.move_count >= a.min_moves_req) and \
            (ses_dat.achscores[a.id] > 0) and \
            all([((ses_dat.guildscores[gr.guild_id] > gr.lim) ^ (not gr.is_min)) for gr in a.reqs_guild]) and \
            all([((ses_dat.params[pr.param_id] > pr.lim) ^ (not pr.is_min)) for pr in a.reqs_param]):
            ses_dat.ach.append(a)
            
            
    
    for dc in ses_dat.sc.deathconds:
        for dcg in dc.cond_guild:
            if ((dcg.is_min) ^ (dcg.lim < ses_dat.guildscores[dcg.guild_id])):
                get_followed_by_end(p, _(dc.message_td) + (_(ses_dat.dial["fin"]).format(ses_dat.scores()) if len(ses_dat.ach) is not 0 else "" ), ses_dat)
                return
        for dcp in dc.cond_param:
            if ((dcp.is_min) ^ (dcp.lim < ses_dat.params[dcp.param_id])):
                get_followed_by_end(p, _(dc.message_td) + (_(ses_dat.dial["fin"]).format(ses_dat.scores()) if len(ses_dat.ach) is not 0 else "" ), ses_dat)
                return
    p.dialogue = _(o.status_td) if o.status_td is not None else ""
    print(p.dialogue)
    if ses_dat.move_count >= len(ses_dat.sc.choices):
        get_followed_by_end(p, _(ses_dat.dial["no_choices"]) + _(ses_dat.dial["fin"]).format(ses_dat.scores()), ses_dat)
    else:
        p.dialogue += _(ses_dat.sc.choices[ses_dat.move_count].question_td)
        for opt in ses_dat.sc.choices[ses_dat.move_count].options:
            p.followed_by([_(ans.answer_td) for ans in opt.answers], Phase("", opt, ses_dat, onspoke=predetermine))
            
def begin(p, ses_dat):
    p.dialogue = _(ses_dat.sc.choices[0].question_td)
    for opt in ses_dat.sc.choices[0].options:
        p.followed_by([_(ans.answer_td) for ans in opt.answers], Phase("", opt, ses_dat, onspoke=predetermine))

def become_hint(p, ses_dat):
    p.dialogue = _(ses_dat.dial["hint"]).format(", ".join(p.ask()[1]))
    


class Phase():
    def __init__(self, dialogue, *args, justpass=False, onspoke=None, confused_dialogue=""):
        self.type=type
        self.onspoke = onspoke
        self.dialogue = dialogue
        self.args = args
        self.next = []
        self.confused_d = confused_dialogue if confused_dialogue is not "" else dialogue
        self.confused_count = 0
        self.justpass = justpass

    def ask(self):
        if self.onspoke:
            self.onspoke(self, *self.args)
        if len(self.next)==1:
            return self.dialogue, self.next[0]["kw"]
        else:
            return self.dialogue, [dir["kw"][0] for dir in self.next]

    def followed_by(self, cdw, phs):
        self.next.append({
            "kw":cdw,
            "phs":phs
            })
        return self

    def answer(self, utterance):
        if len(self.next) == 0:
            return 
        if(self.justpass):
            return self.next[0]["phs"]
        for dir in self.next:
            print(utterance, dir["kw"])
            if utterance in dir["kw"]:
                return dir["phs"]
        if self.confused_count == 0 and self.confused_d is not "":
            self.dialogue = self.confused_d
        self.confused_count += 1
        self.onspoke = None
        return self

    def __repr__(self):
        return f"<Phase {self.dialogue}>"


def _(td):
    if hasattr(td, "text"):
        return td.text
    else:
        return td

class SessionData:

    def __init__(self, sc, dial, utter):
        self.sc = sc
        self.guildscores = {g.id : g.score for g in self.sc.guilds}
        self.params = {p.id : p.score for p in self.sc.params}
        self.achscores = {a.id : a.score for a in self.sc.achievements}
        self.ach = []
        self.move_count = 0
        self.end_session = False
        import random
        random.shuffle(self.sc.choices)
        self.dial = dial
        self.utter = utter

        gs = Phase("", self, onspoke=begin)
        self.phase = Phase(_(dial["rules_q"])).followed_by(
                        _(utter["utt_pos"]), Phase(_(dial["rules"]), justpass=True).followed_by(
                            [], gs)).followed_by(
                        _(utter["utt_neg"]), gs)
                    

    def iterate(self, utter):
        if self.end_session:
            return "session ended", []
        if utter in self.utter["utt_quit"]:
            print("End comes after me")
            get_followed_by_end(self.phase, "you sholdnt see this", self)
            print(self.phase.ask())
        if utter in self.utter["utt_hint"] or self.phase.confused_count>1:
            become_hint(self.phase, self)
        if utter in self.utter["utt_help"]:
            self.phase = Phase(_(self.dial["help"])).followed_by(
                self.utter["utt_repeat"], self.phase
                ).followed_by(self.utter["utt_quit"], None).followed_by(self.utter["utt_hint"], self.phase)
        if self.end_session:
            return "session ended", []
        if utter not in self.utter["utt_repeat"]:
            self.phase = self.phase.answer(utter)
        return self.phase.ask()

    def scores(self):
        achstring = ', '.join([_(a.name_td)+' \n ' + _(a.desc_td) for a in self.ach])
        return f"{achstring}"