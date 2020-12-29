from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

    



class TextData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tts = db.Column(db.String(200))


    def __repr__(self):
        return self.text


def _(t):
    return TextData(text=t)


class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    desc_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    desc_td = db.relationship("TextData", foreign_keys=desc_td_id, lazy="subquery")

    guilds = db.relationship("Guild", backref="scenario", lazy="subquery")
    choices = db.relationship("Choice", backref="scenario", lazy="subquery")
    deathconds = db.relationship("DeathCond", backref="scenario", lazy="subquery")
    params = db.relationship("GlobalParam", backref="scenario", lazy="subquery")
    achievements = db.relationship("Achievement", backref="scenario", lazy="subquery")



    def __repr__(self):
        return (f"<Scenario {self.id} \"{self.name_td}\"\n "
                f"{self.desc_td} \n "
                f"Guilds: {self.guilds}\n "
                f"Params: {self.params}\n "
                f"Lose Conditions: {self.deathconds} \n "
                f"Choices: {self.choices}\n "
                f"Achievements: {self.achievements}>")


    def gen_def_dc(self, lim=0, msg=[]):
        while len(msg) < len(self.guilds):
            msg.append("missing data")
        for g,m in zip(self.guilds, msg):
            self.deathconds.append(DeathCond(message_td=_(m),cond_guild=[DeathCondGuild(guild=g,lim=lim)]))

class Dialogue(db.Model):
    tag = db.Column(db.String(40), primary_key=True)
    td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    td = db.relationship("TextData", lazy="subquery")

class DialUtter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(40))
    text = db.Column(db.String(200))

class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    score = db.Column(db.Float, default=0)

    aff_by =  db.relationship("GuildOptEffect", backref="guild", lazy="subquery")
    weights = db.relationship("ParamGuildWeights", backref="guild", lazy="subquery")

    def __repr__(self):
        return f"<Guild {self.id} \"{self.name_td}\", score={self.score}>"

class GlobalParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    score = db.Column(db.Float)

    weights = db.relationship("ParamGuildWeights", backref="param", lazy="subquery")
    aff_by =  db.relationship("ParamOptEffect", backref="param", lazy="subquery")

    def __repr__(self):
        return f"<Param {self.id} \"{self.name_td}\", score={self.score}. Weights: {[(w.guild.name_td, w.func_param) for w in self.weights]}>"

    def add_weights(self, gs, ws):
        if (len(gs) == len(ws)) and (len(gs)>0):
            self.weights.extend([ParamGuildWeights(guild=self.scenario.g(g), func_param=w) for g, w in zip(gs, ws)])
            return self
        else:
            print("sizes not equal or empty")


class ParamGuildWeights(db.Model):
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"), primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), primary_key=True)
    func_attr_name = db.Column(db.String(40), default="linear")
    func_param = db.Column(db.Float, default=0)
    # TODO: use env var as params maybe? more params anyway
    # TODO: check that param.id==guild.id

class DeathCond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    message_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))

    message_td = db.relationship("TextData", foreign_keys=message_td_id, lazy="subquery")
    cond_guild = db.relationship("DeathCondGuild", backref="death_cond", lazy="subquery")
    cond_param = db.relationship("DeathCondParam", backref="death_cond", lazy="subquery")

    def __repr__(self):
        if len(self.cond_guild) > 0:
            t = self.cond_guild[0].guild.name_td.text+" "+str(self.cond_guild[0].lim)
        else:
            t = self.cond_param[0].param.name_td.text+" "+str(self.cond_param[0].lim)
        return f"DC: {t}"

    

class DeathCondGuild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    guild = db.relationship("Guild")
    lim =  db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

class DeathCondParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    param = db.relationship("GlobalParam")
    lim =  db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    desc_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    desc_td = db.relationship("TextData", foreign_keys=desc_td_id, lazy="subquery")
    score = db.Column(db.Float, default=0)
    min_moves_req = db.Column(db.Integer, default=0)

    aff_by =  db.relationship("AchOptEffect", backref="achievement", lazy="subquery")
    reqs_guild = db.relationship("AchReqGuild", backref="achievement", lazy="subquery")
    reqs_param = db.relationship("AchReqParam", backref="achievement", lazy="subquery")

class AchReqGuild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    guild = db.relationship("Guild")
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

class AchReqParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    param = db.relationship("GlobalParam")
    lim =  db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    question_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    question_td = db.relationship("TextData", foreign_keys=question_td_id, lazy="subquery")

    options = db.relationship("Option", backref="choice", lazy="subquery")

    def __repr__(self):
        return f"<Choice {self.id} {self.question_td}>"



class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"))

    answers = db.relationship("Answer", backref="option", lazy="subquery")

    guild_effects = db.relationship("GuildOptEffect", backref="option", lazy="subquery")
    param_effects = db.relationship("ParamOptEffect", backref="option", lazy="subquery")
    ach_effects = db.relationship("AchOptEffect", backref="option", lazy="subquery")

    status_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    status_td = db.relationship("TextData", lazy="subquery")

    def poe(self, p, e):
        self.param_effects.append(ParamOptEffect(param=p,strength=e))
        return self

    def goe(self, g, e):
        self.guild_effects.append(GuildOptEffect(guild=g,strength=e))
        return self

    def aoe(self, a, e):
        self.ach_effects.append(AchOptEffect(achievement=a,strength=e))
        return self


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"))
    answer_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    answer_td = db.relationship("TextData", foreign_keys=answer_td_id, lazy="subquery")

class ParamOptEffect(db.Model):
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)

class GuildOptEffect(db.Model):
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)

class AchOptEffect(db.Model):
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)

