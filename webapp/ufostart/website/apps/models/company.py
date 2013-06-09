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

class ExpertModel(Mapping):
    linkedinId = TextField()
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    introLinkedinId = TextField()
    introFirstName = TextField()
    introLastName = TextField()
    introPicture = TextField()

    @property
    def expert_picture(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    @property
    def expert_name(self):
        return u"{} {}".format(self.firstName, self.lastName)
    @property
    def intro_name(self):
        return u"{} {}".format(self.introFirstName, self.introLastName)
    @property
    def intro_picture(self):
        return self.introPicture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"



class ServiceModel(Mapping):
    name = TextField()
    url = TextField()
    logo = TextField()
    worker = TextField()
    picture = TextField()
    @property
    def worker_name(self):
        return self.worker
    @property
    def worker_picture(self):
        return self.picture or"//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    @property
    def logo_picture(self):
        return 'http://smartling.99designs.com/static/images/frontpage/logo.png'

class NeedModel(Mapping):
    key = TextField()
    name = TextField()
    category = TextField()

    Service = DictField(ServiceModel)
    Expert = DictField(ExpertModel)

    # TODO: actual implementation
    equity_mix = 4
    @property
    def customized(self):
        return choice([True, False])
    money_value = format_currency(120, 'EUR', locale = 'en')
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

    def getDisplayTags(self):
        return u" • ".join(['Palo Alto', 'Marketplaces', 'Outsourcing'])

    # TODO: actual implementation
    description = 'Democratizing access to scientific expertise'
    logo_picture = None
    product_picture = None
    product_name = 'Serious Watch 5000'
    product_description = 'This watch can measure time just like any other watch, it can tell how much the current time is.'
    no_pledgees = 235
    @property
    def pledgees(self):
        return self.Round.Pledges
    def groupedNeeds(self, n = 4):
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
