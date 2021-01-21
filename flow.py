import random


def get_followed_by_end(phase, text, ses_dat):
    phase.dialogue += text
    phase.justpass = True
    phase.next = []
    phase.onspoke = None

    def die(_, session_data):
        session_data.end_session = True

    phase.followed_by([], Phase(_(ses_dat.dial["goodbye"]), ses_dat, onspoke=die))


def predetermine(phase, option_chosen, session_data):
    session_data.move_count += 1
    for effect in option_chosen.guild_effects:
        session_data.guildscores[effect.guild_id] += effect.strength
    for effect in option_chosen.param_effects:
        session_data.params[effect.param_id] += effect.strength
    for effect in option_chosen.ach_effects:
        session_data.achscores[effect.ach_id] += effect.strength

    for param in session_data.scenario.params:
        for weight in param.weights:
            session_data.guildscores[weight.guild_id] += \
                session_data.params[weight.param_id] * weight.func_param

    for achievement in session_data.scenario.achievements:
        if (achievement not in session_data.ach) and \
                (session_data.move_count >= achievement.min_moves_req) and \
                (session_data.achscores[achievement.id] > 0) and \
                all([((session_data.guildscores[gr.guild_id] > gr.lim) ^
                      (not gr.is_min)) for gr in achievement.reqs_guild]) and \
                all([((session_data.params[pr.param_id] > pr.lim) ^
                      (not pr.is_min)) for pr in achievement.reqs_param]):
            session_data.ach.append(achievement)

    for death_cond in session_data.scenario.deathconds:
        fin_msg = _(death_cond.message_td)
        if not len(session_data.ach) == 0:
            fin_msg += _(session_data.dial["fin"]).format(session_data.scores())
        for dcg in death_cond.cond_guild:
            if (dcg.is_min) ^ (dcg.lim < session_data.guildscores[dcg.guild_id]):
                get_followed_by_end(phase, fin_msg, session_data)
                return
        for dcp in death_cond.cond_param:
            if (dcp.is_min) ^ (dcp.lim < session_data.params[dcp.param_id]):
                get_followed_by_end(phase, fin_msg, session_data)
                return
    phase.dialogue = _(option_chosen.status_td) if option_chosen.status_td is not None else ""
    print(phase.dialogue)
    if session_data.move_count >= len(session_data.scenario.choices):
        msg = _(session_data.dial["no_choices"]) + \
              _(session_data.dial["fin"]).format(session_data.scores())
        get_followed_by_end(phase, msg, session_data)
    else:
        phase.dialogue += _(session_data.scenario.choices[session_data.move_count].question_td)
        for opt in session_data.scenario.choices[session_data.move_count].options:
            phase.followed_by([_(ans.answer_td) for ans in opt.answers],
                              Phase("", opt, session_data, onspoke=predetermine))


def begin(phase, session_data):
    phase.dialogue = _(session_data.scenario.choices[0].question_td)
    for opt in session_data.scenario.choices[0].options:
        phase.followed_by([_(ans.answer_td) for ans in opt.answers],
                          Phase("", opt, session_data, onspoke=predetermine))


def become_hint(phase, session_data):
    phase.dialogue = _(session_data.dial["hint"]).format(", ".join(phase.ask()[1]))


class Phase():
    def __init__(self, dialogue, *args, justpass=False, onspoke=None, confused_dialogue=""):
        self.onspoke = onspoke
        self.dialogue = dialogue
        self.args = args
        self.next = []
        self.confused_d = confused_dialogue if confused_dialogue != "" else dialogue
        self.confused_count = 0
        self.justpass = justpass

    def ask(self):
        if self.onspoke:
            self.onspoke(self, *self.args)
        if len(self.next) == 1:
            return self.dialogue, self.next[0]["kw"]
        return self.dialogue, [dir["kw"][0] for dir in self.next]

    def followed_by(self, cdw, phs):
        self.next.append({
            "kw": cdw,
            "phs": phs
        })
        return self

    def answer(self, utterance):
        if len(self.next) == 0:
            return self
        if self.justpass:
            return self.next[0]["phs"]
        for direction in self.next:
            print(utterance, direction["kw"])
            if utterance in direction["kw"]:
                return direction["phs"]
        if self.confused_count == 0 and self.confused_d != "":
            self.dialogue = self.confused_d
        self.confused_count += 1
        self.onspoke = None
        return self

    def __repr__(self):
        return f"<Phase {self.dialogue}>"


def _(textdata):
    if hasattr(textdata, "text"):
        return textdata.text
    return textdata


class SessionData:

    def __init__(self, sc, dial, utter):
        self.scenario = sc
        self.guildscores = {g.id: g.score for g in self.scenario.guilds}
        self.params = {p.id: p.score for p in self.scenario.params}
        self.achscores = {a.id: a.score for a in self.scenario.achievements}
        self.ach = []
        self.move_count = 0
        self.end_session = False

        random.shuffle(self.scenario.choices)
        self.dial = dial
        self.utter = utter

        gamestart_phase = Phase("", self, onspoke=begin)
        self.phase = Phase(_(dial["rules_q"])).followed_by(
            _(utter["utt_pos"]), Phase(_(dial["rules"]), justpass=True).followed_by(
                [], gamestart_phase)).followed_by(
            _(utter["utt_neg"]), gamestart_phase)

    def iterate(self, utter):
        if self.end_session:
            return "session ended", []
        if utter in self.utter["utt_quit"]:
            print("End comes after me")
            get_followed_by_end(self.phase, "you sholdnt see this", self)
            print(self.phase.ask())
        if utter in self.utter["utt_hint"] or self.phase.confused_count > 1:
            become_hint(self.phase, self)
        if utter in self.utter["utt_help"]:
            self.phase = Phase(_(self.dial["help"])).followed_by(
                self.utter["utt_repeat"], self.phase
            ).followed_by(self.utter["utt_quit"], None).followed_by(
                self.utter["utt_hint"], self.phase)
        if self.end_session:
            return "session ended", []
        if utter not in self.utter["utt_repeat"]:
            self.phase = self.phase.answer(utter)
        return self.phase.ask()

    def scores(self):
        achstring = ', '.join([_(a.name_td) + ' \n ' + _(a.desc_td) for a in self.ach])
        return f"{achstring}"
