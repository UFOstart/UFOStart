# coding=utf-8
from collections import OrderedDict
from datetime import datetime, timedelta
from operator import attrgetter
from random import random, sample
from babel.dates import format_date
from babel.numbers import get_currency_symbol
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField, BooleanField, IntegerField
from hnc.tools.tools import word_truncate_by_letters
from httplib2 import Http
from pyramid.decorator import reify
import simplejson
from ufostart.lib.tools import getYoutubeVideoId, getVimeoVideoId, format_currency
from ufostart.models.tasks import NamedModel
from ufostart.website.apps.models.workflow import WorkflowModel

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




class CompanyUserModel(Mapping):
    token = TextField()
    name = TextField()
    picture = TextField()
    unconfirmed = BooleanField()

    @property
    def picture_url(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

    @property
    def position(self):
        return 'Founder'


class IntroducerModel(Mapping):
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    @property
    def name(self):
        return u"{} {}".format(self.firstName, self.lastName)

    @property
    def position(self):
        return "IT Expert"

class ExpertModel(Mapping):
    linkedinId = TextField()
    firstName = TextField()
    lastName = TextField()
    headline = TextField()
    picture = TextField()
    Introducer = ListField(DictField(IntroducerModel))


    introFirstName = TextField()
    introLastName = TextField()
    introPicture = TextField()

    @property
    def name(self):
        return u"{} {}".format(self.firstName, self.lastName)
    @property
    def position(self):
        return self.headline or 'IT Expert'
    @property
    def display_skills(self):
        return ', '.join(sample(SKILLS, int(random()*30)))
    @property
    def introducers(self):
        return [IntroducerModel(picture = self.introPicture, firstName = self.introFirstName, lastName = self.introLastName)]#self.Introducer

class ServiceModel(Mapping):
    name = TextField()
    description = TextField(default = 'this is a web service')
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
    def logo_url(self):
        return self.logo

class ApplicationModel(Mapping):

    message = TextField()
    created = DateTimeField()
    User = DictField(CompanyUserModel)

    @property
    def display_date(self):
        return format_date(self.created, format='medium', locale='en')




class BaseCompanyModel(Mapping):
    token = TextField()
    slug = TextField()
    name = TextField()
    logo = TextField()
    url = TextField()
    description = TextField()
    @property
    def display_name(self):
        if self.is_setup:
            return self.name
        else:
            return 'Your Company'

    @property
    def is_setup(self):
        return self.slug
    @property
    def logo_url(self):
        return self.logo

class NeedModel(Mapping):
    token = TextField()
    name = TextField()
    summary = TextField()
    status = TextField()
    category = TextField()
    customText = TextField()
    picture = TextField()
    cash = IntegerField(default = 0)
    equity = IntegerField(default = 0)
    Tags = ListField(DictField(NamedModel))
    Applications = ListField(DictField(ApplicationModel))

    Company = DictField(BaseCompanyModel)

    Services = ListField(DictField(ServiceModel))
    Experts = ListField(DictField(ExpertModel))

    @property
    def slug(self):
        return self.token
    @property
    def customized(self):
        return self.status != 'PENDING'
    @property
    def tags(self):
        return map(attrgetter('name'), self.Tags)

    @property
    def total(self):
        return (self.cash or 0) + (self.equity or 0)
    @property
    def equity_ratio(self):
        return int(100.0 * (self.equity or 0) / (self.total or 1))

    @property
    def display_total(self):
        return format_currency(self.total, self.currency)
    @property
    def display_cash(self):
        return format_currency(self.cash, self.currency)
    @property
    def display_equity(self):
        return format_currency(self.equity, self.currency)
    @property
    def display_mix(self):
        return '{}%'.format(self.equity_ratio)



    @property
    def experts(self):
        return self.Experts
    @property
    def services(self):
        return self.Services

    # TODO: actual implementation



    currency = 'USD'
    currency_symbol = get_currency_symbol('USD', locale = 'en')

    _inUse = BooleanField()

class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    Need = ListField(DictField(NeedModel))

    def getStyleKey(self):
        if not self.key:
            self.key = self.name.replace(" ", "_").upper()
        return TEMPLATE_STYLE_KEYS[self.key]

    @reify
    def display_tags(self):
        result = set()
        for need in self.Need:
            result = result.union(set(need.tags))
        return result

    def groupedNeeds(self, n = 4):
        needs = self.Need
        length = len(needs)
        result = OrderedDict()
        for i, need in enumerate(needs):
            l = result.setdefault(i % n, [])
            l.append(need)
        return result.values()



class PledgeModel(Mapping):
    name = TextField()
    network = TextField()
    networkId = TextField()
    picture = TextField()
    offer = TextField()
    comment = TextField()


class EventModel(Mapping):
    name = TextField()
    picture = TextField()
    text = TextField()
    recency =TextField()

class ProductModel(Mapping):
    token = TextField()
    name = TextField()
    picture = TextField()
    video = TextField()
    description = TextField()
    Offers = ListField(DictField(NamedModel))

    @property
    def is_setup(self):
        return self.name and self.token

    @property
    def offers(self):
        return self.Offers

    def getYoutubeVideoId(self):
        if self.video and 'youtube' in self.video:
            return getYoutubeVideoId(self.video)
        return ''

    def getVimeoVideoId(self):
        if self.video and 'vimeo' in self.video:
            return getVimeoVideoId(self.video)
        return ''


class RoundModel(Mapping):
    start = DateTimeField()
    token = TextField()
    status = TextField()
    Needs = ListField(DictField(NeedModel))
    Users = ListField(DictField(CompanyUserModel))
    Pledges = ListField(DictField(PledgeModel))
    Product = DictField(ProductModel)
    Template = DictField(TemplateModel)
    Workflow = DictField(WorkflowModel)
    @reify
    def expiry(self):
        return self.start+timedelta(90)

    def getExpiryDays(self, singular = "{} Day Left", plural="{} Days Left", closed = "Closed"):
        delta = (self.start+timedelta(90)) - datetime.today()
        days = delta.days + 1
        if 0 < days <= 1:
            return singular.format(days)
        elif days > 1:
            return plural.format(days)
        else:
            return closed
    def getExpiryDate(self):
        return format_date(self.start+timedelta(90), format="medium", locale='en')

    @property
    def published(self):
        return self.status == 'PUBLISHED'


class CompanyModel(BaseCompanyModel):
    tagString = TextField()

    angelListId = TextField()
    angelListToken = TextField()


    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))
    Users = ListField(DictField(CompanyUserModel))

    @property
    def currentRound(self):
        return self.Round if self.Round else None

    def isMember(self, userToken):
        if not userToken: return False
        return len(filter(lambda x: x.token == userToken, self.Users))

    @property
    def no_users(self):
        return len(self.Users)

    @property
    def product_is_setup(self):
        try:
            return bool(self.Round.Product.token)
        except AttributeError:
            return False

    @property
    def product_description(self):
        return self.Round.Product.description if self.product_is_setup else ''

    @reify
    def product_pledges(self):
        return len(self.Round.Product.Pledges) if self.product_is_setup else 0

    @reify
    def product_name(self):
        return self.Round.Product.name if self.product_is_setup else ''

    @reify
    def product_picture(self):
        product = self.Round.Product
        if not product: return None
        media = product.video or product.picture
        if not media: return None
        if 'youtube' in media:
            youtubeId  = getYoutubeVideoId(media)
            return 'http://img.youtube.com/vi/{}/0.jpg'.format(youtubeId)
        elif 'vimeo' in media:
            try:
                vimeoId =  getVimeoVideoId(media)
                h = Http()
                resp, data = h.request("http://vimeo.com/api/v2/video/{}.json".format(vimeoId))
                json = simplejson.loads(data)
                return json[0]['thumbnail_small']
            except:
                return None
        else:
            return media

    @property
    def display_tags(self):
        if self.is_setup:
            return self.tagString
        else:
            return ''

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
