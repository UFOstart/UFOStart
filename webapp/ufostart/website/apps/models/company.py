# coding=utf-8
from collections import OrderedDict
from datetime import datetime, timedelta
from operator import attrgetter
from random import random, sample
from babel.dates import format_date
from babel.numbers import get_currency_symbol
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField, BooleanField, IntegerField, DateField, DecimalField
from hnc.tools.tools import word_truncate_by_letters
from httplib2 import Http
from pyramid.decorator import reify
import simplejson
from ufostart.lib.html import getYoutubeVideoId, getVimeoVideoId, getVimeoMeta
from ufostart.lib.tools import format_currency
from ufostart.models.tasks import NamedModel
from ufostart.website.apps.models.workflow import WorkflowModel

TEMPLATE_STYLE_KEYS = {
    'E-COMMERCE':'ecommerce'
    , 'STEVE_BLANK':'hitech'
    , 'SCALE':'seed'
    , 'LAUNCH':'started'
    , 'START':'seriesb'
}


def getRoleName(role):
    return role.title().replace("_", " ")


class CompanyUserModel(Mapping):
    token = TextField()
    name = TextField()
    role = TextField()
    headline = TextField()
    picture = TextField()
    unconfirmed = BooleanField()
    startupValue = IntegerField()

    @property
    def confirmed(self):
        return not self.unconfirmed

    @property
    def picture_url(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

    @property
    def position(self):
        return getRoleName(self.role) if self.role else self.headline
    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue)

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
    def picture_url(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    @property
    def display_skills(self):
        return ', '.join([])
    @property
    def introducers(self):
        if not self.introFirstName: return []
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

    token = TextField()
    message = TextField()
    approved = BooleanField()
    created = DateTimeField()
    User = DictField(CompanyUserModel)

    @property
    def display_date(self):
        return format_date(self.created, format='medium', locale='en')


class PictureModel(Mapping):
    url = TextField()
    def __repr__(self):
        return self.url

class UpdateModel(Mapping):
    text = TextField()
    created = DateTimeField()
    userName = TextField()
    userToken = TextField()
    userHeadline = TextField()
    userPicture = TextField()
    def __repr__(self):
        return self.text

class BaseCompanyModel(Mapping):
    token = TextField()
    slug = TextField()

    url = TextField()

    name = TextField()
    pitch = TextField()
    description = TextField()
    logo = TextField()
    Pictures = ListField(DictField(PictureModel))
    Updates = ListField(DictField(UpdateModel))
    video = TextField()
    slideShare = TextField()

    def getUpdates(self):
        return sorted(self.Updates, key = attrgetter('created'), reverse = True)

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


class EndorsementModel(Mapping):
    endorserToken = TextField()
    endorseeName = TextField()
    endorseeHeadline = TextField()
    endorseeLinkedinId = TextField()
    endorseePicture = TextField()

    @property
    def id(self):
        return self.endorseeLinkedinId
    def getPicture(self):
        return self.endorseePicture
    def getName(self):
        return self.endorseeName
    def getPosition(self):
        return self.endorseeHeadline

class NeedModel(Mapping):
    token = TextField()
    slug = TextField()
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
    Endorsements = ListField(DictField(EndorsementModel))
    Company = DictField(BaseCompanyModel)

    Services = ListField(DictField(ServiceModel))
    Experts = ListField(DictField(ExpertModel))

    @reify
    def applicationMap(self):
        return {a.token:a for a in self.Applications}
    @reify
    def acceptedApplication(self):
        try:
            return [a for a in self.Applications if a.approved][0]
        except IndexError, e:
            return None
    def getRecentApplications(self, n):
        return sorted(self.Applications, key = attrgetter('created'), reverse = True)[:n]

    @property
    def customized(self):
        return self.status != 'PENDING'
    @property
    def fulfilled(self):
        return self.status == 'FULFILED'

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
    offerToken = TextField()
    offerName = TextField()
    comment = TextField()

    def is_native(self):
        return self.network.lower() == 'uf'

    # TODO: implement
    created = datetime(2013,1,1)

class EventModel(Mapping):
    name = TextField()
    picture = TextField()
    text = TextField()
    recency =TextField()


class OfferModel(Mapping):
    token = TextField()
    name = TextField()
    description = TextField()
    stock = IntegerField()
    price = IntegerField()
    @reify
    def display_price(self):
        return format_currency(self.price, 'USD')


class InvestmentModel(Mapping):
    created = DateTimeField()
    amount = IntegerField()
    User = DictField(CompanyUserModel)

    @property
    def display_amount(self):
        return format_currency(self.amount, 'USD')


class FundingModel(Mapping):
    amount = IntegerField(default = 0)
    valuation = IntegerField(default = 0)
    description = TextField()
    Investments = ListField(DictField(InvestmentModel))

    @property
    def display_equity(self):
        return '{}%'.format(self.amount / self.valuation)  if self.valuation else '---'
    @reify
    def invested_amount(self):
        return sum(map(attrgetter('amount'), self.Investments))
    @property
    def display_invested_amount(self):
        return format_currency(self.invested_amount, 'USD')
    @property
    def display_amount(self):
        return format_currency(self.amount, 'USD') if self.amount else '---'
    @property
    def investment_progress(self):
        return "{}%".format(int(100.0 * self.invested_amount / self.amount)) if self.amount else '---'

class ProductModel(Mapping):
    token = TextField()
    name = TextField()
    picture = TextField()
    video = TextField()
    description = TextField()
    Offers = ListField(DictField(OfferModel))
    Pictures = ListField(DictField(PictureModel))
    @property
    def is_setup(self):
        return self.name and self.token

    @property
    def offers(self):
        return self.Offers

    @reify
    def offerMap(self):
        return {o.name:o for o in self.Offers}

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
    Funding = DictField(FundingModel)

    def getPledges(self):
        return sorted(self.Pledges, key = attrgetter('created'), reverse = True)

    @reify
    def expiry(self):
        return self.start+timedelta(90)
    @reify
    def needMap(self):
        return {n.slug:n for n in self.Needs}
    @reify
    def display_name(self):
        return self.Template.name
    @reify
    def expiry_days(self):
        delta = (self.start+timedelta(90)) - datetime.today()
        return delta.days + 1

    def getExpiryDays(self, singular = "{} Day Left", plural="{} Days Left", closed = "Closed"):
        days = self.expiry_days
        if 0 < days <= 1:
            return singular.format(days)
        elif days > 1:
            return plural.format(days)
        else:
            return closed
    def getExpiryDate(self):
        return format_date(self.start+timedelta(90), format="medium", locale='en')
    def getExpiryPercentage(self):
        delta = (self.start+timedelta(90)) - datetime.today()
        return 100.0 * (90-delta.days) / 90
    @property
    def published(self):
        return self.status == 'PUBLISHED'
    @reify
    def pendingApproval(self):
        return self.Workflow.canPublish()
    @reify
    def noFulfilledNeeds(self):
        return len([n for n in self.Needs if n.fulfilled])
    @property
    def noTotalNeeds(self):
        return len(self.Needs)

class CompanyModel(BaseCompanyModel):
    tagString = TextField()

    angelListId = TextField()
    angelListToken = TextField()

    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))
    Users = ListField(DictField(CompanyUserModel))

    @reify
    def startupValue(self):
        return sum(map(attrgetter('startupValue'), self.Users))
    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue)
    @reify
    def memberMap(self):
        return {u.token:u for u in self.Users}

    def isMember(self, userToken):
        if not userToken: return False
        return bool(self.memberMap.get(userToken))
    def isFounder(self, userToken):
        if not userToken: return False
        user = self.memberMap.get(userToken)
        return user.role == 'FOUNDER' if user else False
    def isMentor(self, userToken):
        if not userToken: return False
        user = self.memberMap.get(userToken)
        return user.role == 'MENTOR' if user else False

    @property
    def no_users(self):
        return len(self.Users)

    @reify
    def mentors(self):
        return [u for u in self.Users if u.role == 'MENTOR']

    @property
    def rounds(self):
        return [self.Round]
    @property
    def currentRound(self):
        return self.Round if self.Round else None
    def round_no(self, round):
        return 1

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


    def product_picture(self, request):
        product = self.Round.Product
        if not product: return None
        media = product.video or product.picture
        if not media: return None
        if 'youtube' in media:
            youtubeId  = getYoutubeVideoId(media)
            return 'http://img.youtube.com/vi/{}/0.jpg'.format(youtubeId)
        elif 'vimeo' in media:
            meta = getVimeoMeta(request, media)
            return meta.thumbnail_large if meta else None
        else:
            return media

    @property
    def display_tags(self):
        if self.is_setup:
            return self.tagString
        else:
            return ''

    @property
    def no_pledges(self):
        return len(self.pledgees)
    @property
    def pledgees(self):
        return self.Round and self.Round.Pledges or []

    def groupedNeeds(self, n = 4, customized = False):
        if not self.Round: return []
        needs = [need for need in self.Round.Needs if need.customized == customized]
        length = len(needs)
        if not length: return []
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
    role = TextField()
    inviteToken = TextField()

    @property
    def position(self):
        return getRoleName(self.role)