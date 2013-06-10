# coding=utf-8
from collections import OrderedDict
from datetime import datetime, timedelta
from math import floor
from operator import attrgetter
from random import random, sample, choice
from babel.dates import format_date
from babel.numbers import format_currency
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField, BooleanField
from hnc.apiclient.backend import ClientTokenProc
from pyramid.decorator import reify
from ufostart.lib.tools import group_by_n

TEMPLATE_STYLE_KEYS = {
    'EARLY_STAGE_ECOMMERCE':'ecommerce'
    , 'HI-TECH':'hitech'
    , 'INTERNATIONALISING':'internat'
    , 'JUST_GETTING_STARTED':'started'
    , 'SEED_STAGE':'seed'
    , 'SERIES_B':'seriesb'
}

SKILLS = ['abandon'
        , 'abandoned'
        , 'ability'
        , 'able'
        , 'about'
        , 'above'
        , 'abroad'
        , 'absence'
        , 'absent'
        , 'absolute'
        , 'absolutely'
        , 'absorb'
        , 'abuse'
        , 'academic'
        , 'accent'
        , 'acceptable'
        , 'accept'
        , 'access'
        , 'accident'
        , 'accidental'
        , 'accommodation'
        , 'accompany'
        , 'accordingto'
        , 'account'
        , 'accurate'
        , 'accuse'
        , 'achieve'
        , 'achievement'
        , 'acid'
        , 'acknowledge'
        , 'acquire'
        , 'across'
        , 'act'
        , 'action'
        , 'active'
        , 'activity'
        , 'actor'
        , 'actress'
        , 'actual'
        , 'actually'
        , 'ad'
        , 'adapt'
        , 'add'
        , 'addition'
        , 'additional'
        , 'address'
        , 'adequate'
        , 'adjust'
        , 'admiration'
        , 'admire'
        , 'admit'
        , 'adopt'
        , 'adult'
        , 'advance'
        , 'advanced'
        , 'advantage'
        , 'adventure'
        , 'advert'
        , 'advertise'
        , 'advertisement'
        , 'advertising'
        , 'advice'
        , 'advise'
        , 'affair'
        , 'affect'
        , 'affection'
        , 'afford'
        , 'afraid'
        , 'after'
        , 'afternoon'
        , 'afterwards'
        , 'again'
        , 'against'
        , 'age'
        , 'aged'
        , 'agency'
        , 'agent'
        , 'aggressive'
        , 'ago'
        , 'agree'
        , 'agreement'
        , 'ahead'
        , 'aid'
        , 'aim'
        , 'air'
        , 'aircraft'
        , 'airport'
        , 'alarm'
        , 'alarmed'
        , 'alarming'
        , 'alcohol'
        , 'alcoholic'
        , 'alive'
        , 'all'
        , 'allied'
        , 'allow'
        , 'allright'
        , 'ally'
        , 'almost']



class IntroducerModel(Mapping):
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    @property
    def name(self):
        return u"{} {}".format(self.firstName, self.lastName)

class ExpertModel(Mapping):
    linkedinId = TextField()
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    Introducer = ListField(DictField(IntroducerModel))

    @property
    def name(self):
        return u"{} {}".format(self.firstName, self.lastName)
    @property
    def position(self):
        return 'IT Expert'
    @property
    def display_skills(self):
        return ', '.join(sample(SKILLS, int(random()*30)))
    @property
    def introducers(self):
        return self.Introducer

class ServiceModel(Mapping):
    name = TextField()
    description = TextField()
    url = TextField()
    logo = TextField()

    worker = TextField()
    picture = TextField()

    @property
    def worker_name(self):
        return self.worker
    @property
    def worker_picture(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    @property
    def logo_picture(self):
        return self.logo
    @property
    def short_description(self):
        return self.description

class NeedModel(Mapping):
    key = TextField()
    token = TextField()
    name = TextField()
    status = TextField()
    category = TextField()

    Service = DictField(ServiceModel)
    Expert = DictField(ExpertModel)

    # TODO: actual implementation
    equity_mix = 4
    money_value = format_currency(120, 'EUR', locale = 'en')
    picture = ''


    @property
    def first_level_expert(self):
        expert = ExpertModel(firstName='J.', lastName='of Nazareth', picture='http://lorempixel.com/100/100/people')
        return [expert]*5
    @property
    def second_level_expert(self):
        introducer = IntroducerModel(firstName = 'Intro', lastName='Man', picture='http://lorempixel.com/100/100/people/3')
        expert = ExpertModel(firstName='P.', lastName='of Saulus', picture='http://lorempixel.com/100/100/people/2', Introducer = [introducer]*3)
        return [expert]*2
    @property
    def services(self):
        service = ServiceModel(name='99Designs', description='Design Platform', logo = 'http://smartling.99designs.com/static/images/frontpage/logo.png')
        return [service]*5
    @property
    def customized(self):
        return self.status != 'PENDING'
    @property
    def description(self):
        text = 'Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.'
        length = int(random()*len(text))
        return text[:length]
    @property
    def tags(self):
        tags = ['Online Marketplaces', 'Life Sciences', 'Data Analytics', 'Business Intelligence', 'Enterprise Software', 'Enterprise Software', 'Big Data', 'Government Innovation', 'Simulation', 'E-Commerce', 'Customer Service', 'Education', 'Biotechnology', 'Robotics', 'Aerospace']
        return sample(tags, int(random()*len(tags)))


    _inUse = BooleanField()

class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    Need = ListField(DictField(NeedModel))

    def getStyleKey(self):
        if not self.key:
            self.key = self.name.replace(" ", "_").upper()
        return TEMPLATE_STYLE_KEYS[self.key]


class PledgeModel(Mapping):
    name = TextField()
    network = TextField()
    networkId = TextField()
    picture = TextField()


class CompanyUserModel(Mapping):
    token = TextField()
    name = TextField()
    picture = TextField()
    unconfirmed = BooleanField()

    def getPicture(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

class EventModel(Mapping):
    name = TextField()
    picture = TextField()
    text = TextField()
    recency =TextField()


class RoundModel(Mapping):
    start = DateTimeField()
    token = TextField()
    Needs = ListField(DictField(NeedModel))
    Users = ListField(DictField(CompanyUserModel))
    Pledges = ListField(DictField(PledgeModel))


    @reify
    def expiry(self):
        return self.start+timedelta(90)

    def getExpiryDays(self, singular = "{} Day Left", plural="{} Days Left", closed = "Closed"):
        delta = (self.start+timedelta(90)) - datetime.today()
        if 0 < delta.days <= 1:
            return singular.format(delta.days)
        elif delta.days > 1:
            return plural.format(delta.days)
        else:
            return closed
    def getExpiryDate(self):
        return format_date(self.start+timedelta(90), format="medium", locale='en')

    # TODO: actual implementation
    published = False




class CompanyModel(Mapping):
    token = TextField()
    slug = TextField()
    name = TextField()

    logo_url = TextField()
    angellist_url = TextField()

    angelListId = TextField()
    angelListToken = TextField()


    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))
    Users = ListField(DictField(CompanyUserModel))

    def getCurrentRound(self):
        return self.Round

    @property
    def no_users(self):
        return len(self.Users)

    # TODO: actual implementation

    @property
    def display_name(self):
        if self.is_setup:
            return self.name
        else:
            return 'Your Company'
    @property
    def display_description(self):
        if self.is_setup:
            return self.description
        else:
            return ''
    @property
    def display_tags(self):
        if self.is_setup:
            return u" • ".join(['Palo Alto', 'Marketplaces', 'Outsourcing'])
        else:
            return ''


    @property
    def is_setup(self):
        return bool(self.name)
    product_is_setup = is_setup



    description = 'Democratizing access to scientific expertise'
    logo_picture = None
    product_picture = None
    product_name = 'Product Name'
    product_description = ''
    @property
    def no_pledgees(self):
        return len(self.pledgees)
    @property
    def pledgees(self):
        return self.Round and self.Round.Pledges or []
    def groupedNeeds(self, n = 4):
        if not self.Round: return []
        needs = self.Round.Needs
        length = len(needs)
        result = OrderedDict()
        for i, need in enumerate(needs):
            l = result.setdefault(i % n, [])
            l.append(need)
        return result.values()


class InviteModel(Mapping):
    invitorName = TextField()
    companySlug = TextField()
    companyName = TextField()
    name = TextField()
    inviteToken = TextField()
