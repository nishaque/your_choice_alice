"""
Модуль, в котором описывается логика течения диалога, мгровая логика и класс сессионных объектов.
"""
import random


def get_followed_by_end(phase, text, session_data):
    """
    Делает фазу предпоследней, добавляя к ее диалоговому сообщению текст.
    Последней будет фаза с диалогом, полученным по тегу goodbye из сессионного объекта.
    :param phase: Фаза диалога, которая должна стать предпоследней.
    :param text: Добавленный в конец текст.
    :param session_data: Сессионный объект
    """
    phase.dialogue += text
    phase.justpass = True
    phase.next = []
    phase.onspoke = None

    def die(_, ses_dat):
        """
        Заканчивает сессию.
        :param _: Фаза. Аргумент не используется.
        :param ses_dat: Сессионный объект.
        """
        ses_dat.end_session = True

    phase.followed_by([], Phase(_(session_data.dial["goodbye"]), session_data, onspoke=die))


def predetermine(phase, option_chosen, session_data):
    """
    Осуществляет игровую логику, и устанавливает сообщение фазы и подсказки соответствующе ходу игры
    :param phase: Фаза, состояние которой определяется.
    :param option_chosen: Принятое решение.
    :param session_data: Сессионный объект.
    :return:
    """
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
            if dcg.is_min ^ (dcg.lim < session_data.guildscores[dcg.guild_id]):
                get_followed_by_end(phase, fin_msg, session_data)
                return
        for dcp in death_cond.cond_param:
            if dcp.is_min ^ (dcp.lim < session_data.params[dcp.param_id]):
                get_followed_by_end(phase, fin_msg, session_data)
                return
    phase.dialogue = _(option_chosen.status_td) if option_chosen.status_td is not None else ""
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
    """
    Делает фазу задающей первый вопрос.
    :param phase: Фаза, которая становится фазой первого выбора сценария.
    :param session_data: Сессионный объект
    """
    phase.dialogue = _(session_data.scenario.choices[0].question_td)
    for opt in session_data.scenario.choices[0].options:
        phase.followed_by([_(ans.answer_td) for ans in opt.answers],
                          Phase("", opt, session_data, onspoke=predetermine))


def become_hint(phase, session_data):
    """
    Изменяет диалоговое сообщение фазы на подсказку.
    :param phase: Фаза, которая должна стать подсказкой.
    :param session_data: Сессионный объект
    """
    phase.dialogue = _(session_data.dial["hint"]).format(", ".join(phase.ask()[1]))


class Phase:
    """
    Фаза диалога.

    dialogue - сообщение, передаваемое пользователю
    onspoke - ф-я, вызываемая перед тем как выдать пользователю
    сообщение с аргументами self, *self.args. Название аттрибута
    неточно - ф-я вызывается до вывода сообщения, а не после,
    это позволяет функцией изменить диалоговое сообщение, и только
    затем выдать его пользователю.
    next - [{"kw": [Ответы],
             "phs": Фаза, на которую переходит диалог после соответствующего ответа}, ...]
    confused_d - сообщение, выводимое, если на ответ пользователя
    не нашлось подходящего продолжения
    confused_count - число раз подряд, которое пользователь
    сказал что-то не предусмотренное фазой
    justpass - если этот аттрибут True, то при любом ответе фаза
    перейдет по первому направлению в списке next
    """
    def __init__(self, dialogue, *args, justpass=False, onspoke=None, confused_dialogue=""):
        """
        Конструктор, см. документацию класса
        """
        self.onspoke = onspoke
        self.dialogue = dialogue
        self.args = args
        self.next = []
        self.confused_d = confused_dialogue if confused_dialogue != "" else dialogue
        self.confused_count = 0
        self.justpass = justpass

    def ask(self):
        """
        Вызывает onspoke с аргументами self, *self.args
        :return: (Диалоговое сообщение, Список кнопок-подсказок)
        """
        if self.onspoke:
            self.onspoke(self, *self.args)
        if len(self.next) == 1:
            return self.dialogue, self.next[0]["kw"]
        return self.dialogue, [direction["kw"][0] for direction in self.next]

    def followed_by(self, triggers, phase):
        """
        Добавляет вариант ветвления диалога
        :param triggers: [Ответы, означающие, что нужно перейти к указанной фазе]
        :param phase: Фаза, наступающая при одном из перечисленных ответов
        :return: Эту фазу, что позволяет выстраивать вызов этого метода в цепочки
        """
        self.next.append({
            "kw": triggers,
            "phs": phase
        })
        return self

    def answer(self, utterance):
        """
        Получить следующую фазу диалога, основываясь на высказывании пользователя.
        :param utterance: Высказывание пользователя
        :return: Следующая фаза
        """
        if len(self.next) == 0:
            return self
        if self.justpass:
            return self.next[0]["phs"]
        for direction in self.next:
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
    """
    Обертка для получения текста из объектов TextData, сокращение textdata.text
    Использование этой функции позволяет в будущем перейти на использование
    TextData вместо строк с лишь незначительным изменением кода и упростить
    использование tts и локализацию.
    """
    if hasattr(textdata, "text"):
        return textdata.text
    return textdata


class SessionData:
    """
    Класс, в котором хранятся данные о сессии одного пользователя.

    scenario - ORM-объект сценария
    guildscores - показатели гильдий
    params - показатели параметров
    achscores - показатели достижений
    ach - [полученные достижения]
    move_count - число сделанных ходов
    end_session - закончена ли игра
    dial - dict с диалоговыми сообщениями, не привязанными к сценарию
    utter - dict с ожидаемыми сообщениями от пользователя, не привязанными к сценарию
    phase - текущая фаза диалога
    """
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
        """
        Обработать сказанное пользователем и вернуть сообщение и список снопок-подсказок
        :param utter: Сказанное пользователем
        :return: (Сообщение, [Кнопки])
        """
        if self.end_session:
            return "session ended", []
        if utter in self.utter["utt_quit"]:
            get_followed_by_end(self.phase, "you sholdnt see this", self)

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
        """
        Получить список достижений в текстовой форме.
        :return: Список достижений в текстовой форме.
        """
        achstring = ', '.join([_(a.name_td) + ' \n ' + _(a.desc_td) for a in self.ach])
        return achstring
