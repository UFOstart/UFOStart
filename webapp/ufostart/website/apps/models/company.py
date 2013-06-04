from datetime import datetime, timedelta
from babel.dates import format_date
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField, BooleanField
from hnc.apiclient.backend import ClientTokenProc
from pyramid.decorator import reify

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

    def getExpertPicture(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def getExpertName(self):
        return u"{} {}".format(self.firstName, self.lastName)

    def getIntroName(self):
        return u"{} {}".format(self.introFirstName, self.introLastName)
    def getIntroPicture(self):
        return self.introPicture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"



class ServiceModel(Mapping):
    name = TextField()
    url = TextField()
    worker = TextField()
    picture = TextField()
    def getWorkerName(self):
        return self.worker
    def getWorkerPicture(self):
        return self.picture or"//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

class NeedModel(Mapping):
    key = TextField()
    name = TextField()
    category = TextField()
    description = TextField()
    Service = DictField(ServiceModel)
    Expert = DictField(ExpertModel)


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


    def getPledgeEvent(self):
        if len(self.Pledges):
            event = self.Pledges[0]
            return EventModel(name = event.name, picture=event.picture, text = "just pledged to this project", recency = "1 hour ago")
        else: return None

    def getTaskProgress(self):
        return 30 if len(self.Needs) else 0
    def getTaskEvent(self):
        if len(self.Needs):
            evt = EventModel(name = None, picture=None, text = "just pledged to this project", recency = "1 hour ago")
            for need in self.Needs:
                if need.Expert:
                    evt.name = need.Expert.getIntroName()
                    evt.picture = need.Expert.getIntroPicture()
                    evt.text = 'can introduce you'
            if not evt.name:
                for need in self.Needs:
                    if need.Service:
                        evt.name = need.Service.getWorkerName()
                        evt.picture = need.Service.getWorkerPicture()
                        evt.text = 'can use <a href="{}" target="_blank">{}</a> for you'.format(need.Service.url, need.Service.name)
            if evt.name: return evt

    def getAssetsEvent(self):
        return None
    def getMoneyEvent(self):
        return None


class CompanyModel(Mapping):
    token = TextField()
    slug = TextField()
    name = TextField()
    description = TextField()
    angelListId = TextField()
    angelListToken = TextField()


    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))
    Users = ListField(DictField(CompanyUserModel))

    def getCurrentRound(self):
        return self.Round





class InviteModel(Mapping):
    invitorName = TextField()
    companySlug = TextField()
    companyName = TextField()
    name = TextField()
    inviteToken = TextField()
