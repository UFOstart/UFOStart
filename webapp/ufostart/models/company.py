# coding=utf-8
from collections import OrderedDict
from datetime import datetime, timedelta
from operator import attrgetter
from babel.dates import format_date
from babel.numbers import get_currency_symbol, format_decimal
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField, BooleanField, IntegerField
from pyramid.decorator import reify
from ufostart.lib.html import getYoutubeVideoId, getVimeoVideoId, getVimeoMeta
from ufostart.lib.tools import format_currency
from ufostart.models.tasks import NamedModel
from ufostart.models.workflow import WorkflowModel

TEMPLATE_KEYS = {
    'E-COMMERCE':{'key':'ecommerce', 'name':'E-Commerce'}
    , 'STEVE_BLANK':{'key':'hitech', 'name':'Steve Blank'}
    , 'SCALE':{'key':'seed', 'name':'Looking to scale'}
    , 'LAUNCH':{'key':'started', 'name':'About to launch'}
    , 'START':{'key':'seriesb', 'name':'Just getting started'}
}


STANDARD_RUN_TIME = 30

def getRoleName(role):
    return role.title().replace("_", " ")

def default_user_pic(attr):
    def picture_url(self):
        return getattr(self, attr) or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    return picture_url

class CompanyUserModel(Mapping):
    token = TextField()
    slug = TextField()
    name = TextField()
    role = TextField()
    headline = TextField()
    picture = TextField()
    picture_url = property(default_user_pic('picture'))

    unconfirmed = BooleanField()
    startupValue = IntegerField()

    @property
    def isMentor(self):
        return self.role == "MENTOR"
    @property
    def isFounder(self):
        return self.role == "FOUNDER"
    @property
    def isTeamMember(self):
        return self.role in ["FOUNDER", "TEAM_MEMBER"]

    @property
    def confirmed(self):
        return not self.unconfirmed

    @property
    def position(self):
        return getRoleName(self.role) if self.role else self.headline
    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue, 'EUR')

class IntroducerModel(Mapping):
    linkedinId = TextField()
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    picture_url = property(default_user_pic('picture'))

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
    picture_url = property(default_user_pic('picture'))
    Introducer = ListField(DictField(IntroducerModel))


    introFirstName = TextField()
    introLastName = TextField()
    introPicture = TextField()
    introLinkedinId = TextField()

    @property
    def name(self):
        return u"{} {}".format(self.firstName, self.lastName)

    @property
    def position(self):
        return self.headline or 'IT Expert'
    @property
    def display_skills(self):
        return ', '.join([])
    @property
    def introducers(self):
        if not self.introFirstName: return []
        return [IntroducerModel(picture = self.introPicture, firstName = self.introFirstName, lastName = self.introLastName, linkedinId = self.introLinkedinId)]#self.Introducer

class ServiceModel(Mapping):
    name = TextField()
    description = TextField()
    url = TextField()
    logo = TextField()

    worker = TextField()
    picture = TextField()
    picture_url = property(default_user_pic('picture'))

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
    userSlug = TextField()
    userHeadline = TextField()
    userPicture = TextField()
    picture_url = property(default_user_pic('userPicture'))
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
    endorserSlug = TextField()
    endorserToken = TextField()
    endorseeName = TextField()
    endorseeHeadline = TextField()
    endorseeLinkedinId = TextField()
    endorseePicture = TextField()
    picture_url = property(default_user_pic('endorseePicture'))
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
    key = TextField()
    name = TextField()

    _inUse = BooleanField()
    summary = TextField()
    status = TextField()
    category = TextField()
    customText = TextField()
    picture = TextField()
    cash = IntegerField()
    equity = IntegerField()
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
    def added(self):
        return self.status in ['ADDED', 'CUSTOMISED', 'FULFILED']
    @property
    def customized(self):
        return self.status == 'CUSTOMISED'
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


    def display_total(self, currency):
        return format_currency(self.total, currency)
    def display_cash(self, currency):
        return format_currency(self.cash, currency)
    def display_equity_value(self, currency):
        return format_currency(self.equity, currency)
    @property
    def display_mix(self):
        return '{}%'.format(self.equity_ratio)



    @property
    def experts(self):
        return self.Experts
    @property
    def services(self):
        return self.Services


class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    logo = TextField()
    picture = TextField()
    description = TextField()
    Need = ListField(DictField(NeedModel))


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
    slug = property(attrgetter('networkId'))
    confirmed = True
    picture = TextField()
    picture_url = property(default_user_pic('picture'))
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
    picture_url = property(default_user_pic('picture'))
    text = TextField()
    recency =TextField()


class OfferModel(Mapping):
    token = TextField()
    name = TextField()
    description = TextField()
    stock = IntegerField()
    price = IntegerField()


class InvestmentModel(Mapping):
    created = DateTimeField()
    amount = IntegerField()
    User = DictField(CompanyUserModel)

    def display_amount(self, currency):
        return format_currency(self.amount, currency)


class FundingModel(Mapping):
    amount = IntegerField(default = 0)
    valuation = IntegerField(default = 0)
    description = TextField()
    contract = TextField()
    Investments = ListField(DictField(InvestmentModel))

    @property
    def display_equity(self):
        return '{}%'.format(format_decimal(100.0 * self.amount / self.valuation, format='#,###.##', locale='en'))  if self.valuation else '0%'
    @reify
    def invested_amount(self):
        return sum(map(attrgetter('amount'), self.Investments))

    def display_invested_amount(self, currency):
        return format_currency(self.invested_amount, currency)
    def display_amount(self, currency):
        return format_currency(self.amount, currency)

    @property
    def investment_progress(self):
        return "{}%".format(int(100.0 * self.invested_amount / self.amount)) if self.amount else '0%'

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
        return self.start+timedelta(STANDARD_RUN_TIME)
    @reify
    def needMap(self):
        return {n.slug:n for n in self.Needs}
    @reify
    def display_name(self):
        return self.Template.name
    @reify
    def expiry_days(self):
        delta = (self.start+timedelta(STANDARD_RUN_TIME)) - datetime.today()
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
        return format_date(self.start+timedelta(STANDARD_RUN_TIME), format="medium", locale='en')
    def getExpiryPercentage(self):
        delta = (self.start+timedelta(STANDARD_RUN_TIME)) - datetime.today()
        return 100.0 * (STANDARD_RUN_TIME-delta.days) / STANDARD_RUN_TIME
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
        return len([n for n in self.Needs if n.added])


    @property
    def roundTasks(self):
        return filter(attrgetter("customized"), self.Needs)

class CompanyModel(BaseCompanyModel):
    tagString = TextField()

    angelListId = TextField()
    angelListToken = TextField()
    currency = TextField()
    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))
    Users = ListField(DictField(CompanyUserModel))

    @reify
    def startupValue(self):
        return sum(map(attrgetter('startupValue'), self.Users))
    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue, 'EUR')
    @reify
    def memberMap(self):
        return {u.token:u for u in self.Users}

    @property
    def currency_symbol(self):
        return get_currency_symbol(self.currency, 'en')

    def isMember(self, userToken):
        if not userToken: return False
        member = self.memberMap.get(userToken)
        return member and not member.unconfirmed

    def isFounder(self, userToken):
        if not userToken: return False
        user = self.memberMap.get(userToken)
        return user and user.isFounder and not user.unconfirmed

    def isMentor(self, userToken):
        if not userToken: return False
        user = self.memberMap.get(userToken)
        return user and user.isMentor and not user.unconfirmed

    @property
    def no_users(self):
        return len(self.Users)

    @reify
    def mentorTokens(self):
        return set([m.token for m in self.mentors])

    @reify
    def mentors(self):
        return [u for u in self.Users if u.isMentor]
    @reify
    def members(self):
        if len(self.Users) == 1: return []
        return sorted([u for u in self.Users if u.isTeamMember], key = attrgetter('role'))

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
        video = product.video
        if video:
            if 'youtube' in video:
                youtubeId  = getYoutubeVideoId(video)
                return 'http://img.youtube.com/vi/{}/0.jpg'.format(youtubeId)
            elif 'vimeo' in video:
                meta = getVimeoMeta(request, video)
                return meta.thumbnail_large if meta else None
            else: return video
        elif product.picture:
            return product.picture
        elif product.Pictures:
            return product.Pictures[0]
        else: return ''

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
