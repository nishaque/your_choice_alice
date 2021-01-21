from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class TextData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tts = db.Column(db.String(200))

    def __repr__(self):
        return self.text


def _(text):
    return TextData(text=text)


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

    aff_by = db.relationship("GuildOptEffect", backref="guild", lazy="subquery")
    weights = db.relationship("ParamGuildWeights", backref="guild", lazy="subquery")


class GlobalParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    score = db.Column(db.Float)

    weights = db.relationship("ParamGuildWeights", backref="param", lazy="subquery")
    aff_by =  db.relationship("ParamOptEffect", backref="param", lazy="subquery")


class ParamGuildWeights(db.Model):
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"), primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), primary_key=True)
    func_attr_name = db.Column(db.String(40), default="linear")
    func_param = db.Column(db.Float, default=0)


class DeathCond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    message_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))

    message_td = db.relationship("TextData", foreign_keys=message_td_id, lazy="subquery")
    cond_guild = db.relationship("DeathCondGuild", backref="death_cond", lazy="subquery")
    cond_param = db.relationship("DeathCondParam", backref="death_cond", lazy="subquery")


class DeathCondGuild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    guild = db.relationship("Guild")


class DeathCondParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    param = db.relationship("GlobalParam")


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    desc_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    desc_td = db.relationship("TextData", foreign_keys=desc_td_id, lazy="subquery")
    score = db.Column(db.Float, default=0)
    min_moves_req = db.Column(db.Integer, default=0)

    aff_by = db.relationship("AchOptEffect", backref="achievement", lazy="subquery")
    reqs_guild = db.relationship("AchReqGuild", backref="achievement", lazy="subquery")
    reqs_param = db.relationship("AchReqParam", backref="achievement", lazy="subquery")


class AchReqGuild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    guild = db.relationship("Guild")


class AchReqParam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    param = db.relationship("GlobalParam")


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    question_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    question_td = db.relationship("TextData", foreign_keys=question_td_id, lazy="subquery")

    options = db.relationship("Option", backref="choice", lazy="subquery")


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"))
    status_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    status_td = db.relationship("TextData", lazy="subquery")

    answers = db.relationship("Answer", backref="option", lazy="subquery")
    guild_effects = db.relationship("GuildOptEffect", backref="option", lazy="subquery")
    param_effects = db.relationship("ParamOptEffect", backref="option", lazy="subquery")
    ach_effects = db.relationship("AchOptEffect", backref="option", lazy="subquery")


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
