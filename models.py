"""
Модуль, описывающий SQLAlchemy.ORM модели таблиц, использующиеся в базе данных.

Описание полей идентификаторов пропущено.
Вместо полей, хранящих идентификаторы записей в таблице TextData, описаны
SQLAlchemy-аттрибуты, напрямую обращающиеся к объектам TextData.
"""

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class TextData(db.Model):
    """
    Таблица, с помощью которой каждой строке, использованной в игре,
    ставится в соответствие ее TTS-представление.

    text - текстовое представление
    tts - text-to-speech представление
    """
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tts = db.Column(db.String(200))

    def __repr__(self):
        return self.text


class Scenario(db.Model):
    """
    Таблица, описывающая игровой сценарий. Включает:

    name_td - название
    desc_td - описание
    """
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
    """
    Таблица, где без привязки к сценарию хранятся фразы для общения с пользователем.

    tag - уникальный тег фразы
    td - фраза
    """
    tag = db.Column(db.String(40), primary_key=True)
    td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    td = db.relationship("TextData", lazy="subquery")


class DialUtter(db.Model):
    """
    Таблица, хранящая ожидаемые от пользователя команды, не привязанные к сценарию.
    """
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(40))
    text = db.Column(db.String(200))


class Guild(db.Model):
    """
    Таблица, хранящая информацию о гильдиях данного сценария.

    scenario_id - идентификатор сценария
    name_td - название
    score - изначальный показатель
    """
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    score = db.Column(db.Float, default=0)

    aff_by = db.relationship("GuildOptEffect", backref="guild", lazy="subquery")
    weights = db.relationship("ParamGuildWeights", backref="guild", lazy="subquery")


class GlobalParam(db.Model):
    """
    Таблица, хранящая информацию о параметрах данного сценария.

    scenario_id - идентификатор сценария
    name_td - название
    score - изначальный показатель
    """
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    name_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    name_td = db.relationship("TextData", foreign_keys=name_td_id, lazy="subquery")
    score = db.Column(db.Float)

    weights = db.relationship("ParamGuildWeights", backref="param", lazy="subquery")
    aff_by = db.relationship("ParamOptEffect", backref="param", lazy="subquery")


class ParamGuildWeights(db.Model):
    """
    Таблица, хранящая информацию о силе влияния параметров на гильдии в конце хода.

    param_id - идентификатор параметра
    guild_id - идентификатор гильдии
    func_param - численный показатель влияния
    """
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"), primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), primary_key=True)
    func_param = db.Column(db.Float, default=0)


class DeathCond(db.Model):
    """
    Таблица, хранящая информацию о ситуациях, в которых игрок проигрывает.

    scenario_id - идентификатор сценария
    message_td - сообщение для пользователя
    """
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    message_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    message_td = db.relationship("TextData", foreign_keys=message_td_id, lazy="subquery")

    cond_guild = db.relationship("DeathCondGuild", backref="death_cond", lazy="subquery")
    cond_param = db.relationship("DeathCondParam", backref="death_cond", lazy="subquery")


class DeathCondGuild(db.Model):
    """
    Таблица, хранящая информацию об условиях поражения, связанных с гильдиями.

    cond_id - идентификатор DeathCond
    guild_id - идентификатор гильдии
    lim - предельно допустимое значение
    is_min - булевое поле, сообщающее, является ли предел минимумом или
    максимумом (при True - минимум)
    """
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    guild = db.relationship("Guild")


class DeathCondParam(db.Model):
    """
    Таблица, хранящая информацию об условиях поражения, связанных с параметрами.

    cond_id - идентификатор DeathCond
    param_id - идентификатор параметра
    lim - предельно допустимое значение
    is_min - булевое поле, сообщающее, является ли предел минимумом или
    максимумом (при True - минимум)
    """
    id = db.Column(db.Integer, primary_key=True)
    cond_id = db.Column(db.Integer, db.ForeignKey("death_cond.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    param = db.relationship("GlobalParam")


class Achievement(db.Model):
    """
    Таблица, хранящая информацию о доступных к получению достижениях для данного сценария.

    scenario_id - идентификатор сценария.
    name_td - название
    desc_td - описание
    score - число очков достижения, необходимых для его получения, взятое со знаком минус
    min_moves_req - минимальное число ходов для получения достижения
    """
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
    """
    Таблица, хранящая информацию об условиях получения достижения, связанных с гильдиями.

    ach_id - идентификатор достижени
    guild_id - идентификатор гильдии
    lim - предельно допустимое значение
    is_min - булевое поле, сообщающее, является ли предел минимумом или
    максимумом (при True - минимум)
    """
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    guild = db.relationship("Guild")


class AchReqParam(db.Model):
    """
    Таблица, хранящая информацию об условиях получения достижения,
    связанных с параметрами.

    ach_id - идентификатор достижения
    param_id - идентификатор параметра
    lim - предельно допустимое значение
    is_min - булевое поле, сообщающее, является ли предел минимумом или максимумом
    (при True - минимум)
    """
    id = db.Column(db.Integer, primary_key=True)
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"))
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"))
    lim = db.Column(db.Float, default=0)
    is_min = db.Column(db.Boolean, default=True)

    param = db.relationship("GlobalParam")


class Choice(db.Model):
    """
    Таблица, хранящая информацию о предложенных игроку выборах в данном сценарии.

    scenario_id - идентификатор сценария
    question_td - вопрос
    """
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenario.id"))
    question_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    question_td = db.relationship("TextData", foreign_keys=question_td_id, lazy="subquery")

    options = db.relationship("Option", backref="choice", lazy="subquery")


class Option(db.Model):
    """
    Таблица, хранящая информацию о вариантах, которые игрок может выбрать в данном выборе.

    choice_id - идентификатор выбора
    status_td - сообщение о последствиях решения
    """
    id = db.Column(db.Integer, primary_key=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"))
    status_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    status_td = db.relationship("TextData", lazy="subquery")

    answers = db.relationship("Answer", backref="option", lazy="subquery")
    guild_effects = db.relationship("GuildOptEffect", backref="option", lazy="subquery")
    param_effects = db.relationship("ParamOptEffect", backref="option", lazy="subquery")
    ach_effects = db.relationship("AchOptEffect", backref="option", lazy="subquery")


class Answer(db.Model):
    """
    Таблица, хранящая информацию о том, какие ответы пользователя могут
    означать выбор данного варианта.

    option_id - идентификатор варианта
    answer_td - ответ
    """
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"))
    answer_td_id = db.Column(db.Integer, db.ForeignKey("text_data.id"))
    answer_td = db.relationship("TextData", foreign_keys=answer_td_id, lazy="subquery")


class ParamOptEffect(db.Model):
    """
    Таблица, хранящая информацию о том, как варианты выбора влияют на показатели параметров

    param_id - идентификатор параметра
    option_id - идентификатор варианта
    strength - численное воздействие на показатель
    """
    param_id = db.Column(db.Integer, db.ForeignKey("global_param.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)


class GuildOptEffect(db.Model):
    """
    Таблица, хранящая информацию о том, как варианты выбора влияют на показатели гильдий

    guild_id - идентификатор гильдии
    option_id - идентификатор варианта
    strength - численное воздействие на показатель
    """
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)


class AchOptEffect(db.Model):
    """
    Таблица, хранящая информацию о том, как варианты выбора влияют на получение достижений

    ach_id - идентификатор достижения
    option_id - идентификатор варианта
    strength - численное воздействие на показатель
    """
    ach_id = db.Column(db.Integer, db.ForeignKey("achievement.id"), primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("option.id"), primary_key=True)
    strength = db.Column(db.Float, default=0)
