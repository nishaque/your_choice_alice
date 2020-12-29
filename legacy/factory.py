from app import db
from models import *

def _(t):
    return TextData(text=t)

class Factory:

    def d(**kwargs):
        return [Dialogue(tag=tag, td=_(kwargs[tag])) for tag in kwargs]

    def du(**kwargs):
        return [DialUtter(tag=tag, text=t) for tag in kwargs for t in kwargs[tag]]

    def __init__(self, t, d):
        self.s = Scenario(name_td=_(t), desc_td=_(d))
        self.mapping = dict()

    def g(self, t, s):
        self.lastg = Guild(name_td=_(t), score=s, scenario=self.s)
        self.mapping[t] = self.lastg

    def p(self, t, s):
        self.lastp = GlobalParam(name_td=_(t), score=s, scenario=self.s)
        self.mapping[t] = self.lastp

    def w(self, ws, use_map=False):
        if use_map:
            target=self.mapping[use_map]
        else:
            target=self.lastp
        target.weights = [ParamGuildWeights(guild=gu, func_param=w) for gu, w in zip(self.s.guilds, ws)]

    def a(self, t, d, sc, mm=0):
        self.lasta = Achievement(name_td=_(t), desc_td=_(d), score=-sc, scenario=self.s, min_moves_req=mm)
        self.mapping[t] = self.lasta

    def c(self, t):
        self.mapping[t] = self.lastc = Choice(question_td=_(t), scenario=self.s)

    def o(self, a, *aa, use_map=False):
        if use_map:
            target = self.mapping[use_map]
        else:
            target = self.lastc

        self.lasto = Option(choice=target, answers=[Answer(answer_td=_(a))])

        for an in aa:
            self.lasto.append(Answer(answer_td=_(an)))
            
    def og(self, g, s):
        return self.lasto.goe(self.s.guilds[g], s)
    def op(self, p, s):
        return self.lasto.poe(self.s.params[p], s)
    def oa(self, a, s):
        return self.lasto.aoe(self.s.achievements[a], s)

    def ans(self, answs):
        self.lasto.answers.extend([Answer(answer_td=_(answ)) for answ in answs])

    def oall(self, st, gefs, pefs, aefs):
        self.lasto.status_td = _(st)
        for gu, e in zip(range(len(self.s.guilds)), gefs):
            self.og(gu, e)
        for pa, e in zip(range(len(self.s.params)), pefs):
            self.op(pa, e)
        for ach, e  in aefs:
            self.oa(ach, e)

    def dcg(self, t, lim=0, use_map=False):
        if use_map:
            target = self.mapping[use_map]
        else:
            target = self.lastg
        self.mapping[t] = self.lastdcg = DeathCond(message_td=_(t), cond_guild=[DeathCondGuild(guild=target, lim=lim)], scenario=self.s)

    def dcp(self, t, lim=0, is_min=True, use_map=False):
        if use_map:
            target = self.mapping[use_map]
        else:
            target = self.lastp
        self.mapping[t] = self.lastdcp = DeathCond(message_td=_(t), cond_param=[DeathCondParam(param=target, lim=lim, is_min=is_min)], scenario=self.s)

    








