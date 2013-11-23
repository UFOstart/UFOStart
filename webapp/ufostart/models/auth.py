from datetime import datetime
from operator import attrgetter
from hnc.apiclient import Mapping, TextField, IntegerField, ListField, DictField, DateTimeField
from pyramid.decorator import reify
from pyramid.security import has_permission
import simplejson
from ufostart.lib.html import format_date
from ufostart.lib.tools import format_currency
from ufostart.models.tasks import NamedModel
from ufostart.models.company import CompanyModel, ApplicationModel




class SocialNetworkProfileModel(Mapping):
    id = TextField()
    network = TextField()
    picture = TextField()
    name = TextField()
    email = TextField()
    accessToken = TextField()
    secret = TextField()
    original = DictField()



SOCIAL_NETWORK_TYPES = {'LI':'linkedin', 'FB':'facebook', 'AL':'angellist', 'XI':'xing', 'TW':'twitter'}
SOCIAL_NETWORK_TYPES_REVERSE = {v:k for k,v in SOCIAL_NETWORK_TYPES.items()}



class WebUserNetworkProfile(SocialNetworkProfileModel):
    type = TextField()

    def inferredNetwork(self):
        return SOCIAL_NETWORK_TYPES[self.type]


class UserApplicationModel(ApplicationModel):
    comapnyLogo = TextField()
    companyName = TextField()
    companyToken = TextField()
    companySlug = TextField()
    need = TextField()
    needToken = TextField()
    needSlug = TextField()
    created = DateTimeField()

    @property
    def display_date(self):
        return format_date(self.created, format='medium')

class UserEndorsementsModel(Mapping):
    created = DateTimeField()
    endorserPicture = TextField()
    endorserName = TextField()
    endorserSlug = TextField()
    endorserToken = TextField()
    endorserHeadline = TextField()

    needName = TextField()
    needSlug = TextField()
    companyName = TextField()
    companySlug = TextField()

    @property
    def display_date(self):
        return format_date(self.created, format='medium')

class UserModel(Mapping):
    UserGroups = ['WebUser']
    token = TextField()
    slug = TextField()
    name = TextField()
    pwd = TextField()
    email = TextField()
    headline = TextField()
    picture = TextField()

    startupValue = IntegerField()
    investmentAmount = IntegerField()
    currency = TextField()
    interests = TextField()

    fbLink = TextField()
    xingLink = TextField()
    @property
    def liLink(self):
        liProfile = [n for n in self.Profile if n.type == 'LI'][0]
        return 'http://www.linkedin.com/profile/view?id={}'.format(liProfile['id'])


    Skills = ListField(DictField(NamedModel))
    Profile = ListField(DictField(WebUserNetworkProfile))
    Company = DictField(CompanyModel)
    Companies = ListField(DictField(CompanyModel))
    Applications = ListField(DictField(UserApplicationModel))
    Endorsements = ListField(DictField(UserEndorsementsModel))


    # mockMember
    picture_url = property(attrgetter('picture'))
    confirmed = True

    def isAnon(self):
        return self.token is None
    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True).copy()
        json.pop("Profile", None)
        json.pop("Companies", None)
        json.pop("Company", None)
        json.pop("Applications", None)
        json.pop("Endorsements", None)
        return simplejson.dumps(json) if stringify else json

    def getSocialProfileJSON(self, stringify = True):
        result = {n.inferredNetwork():n.unwrap(sparse = True) for n in self.Profile if n.id}
        return simplejson.dumps(result) if stringify else result

    def getEndorsements(self):
        return self.Endorsements

    def isMe(self, network, id):
        map = {n.inferredNetwork():n.id for n in self.Profile if n.id}
        netId = map.get(network)
        return netId == id

    @property
    def displayInvestment(self):
        return format_currency(self.investmentAmount, self.currency)


    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue, 'EUR')
    def getPicture(self):
        if self.picture:
            return self.picture
        else:
            pics = [p.picture for p in self.Profile if p.picture]
            if len(pics):
                return pics[0]
            else:
                return "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def getDefaultCompanySlug(self):
        return self.Company.slug if self.Company else None
    def getDefaultCompanyName(self):
        return self.Company.name if self.Company else None

    @reify
    def mentoredStartups(self):
        return [c for c in self.Companies if c.isMentor(self.token)]

    @reify
    def profileMap(self):
        return {n.network:n for n in self.Profile}

    @property
    def position(self):
        return self.headline

    @property
    def display_skills(self):
        if self and self.Skills:
            return map(attrgetter('name'), self.Skills)
        else:
            return ''
    @property
    def displayStartupValue(self):
        return format_currency(self.startupValue, 'EUR')

def AnonUser():
    return UserModel()



USER_TOKEN = "USER_TOKEN"

def canEdit(self): return has_permission('edit', self, self.request)
def getUser(self):
    return self.request.session.get(USER_TOKEN) or UserModel()
def setUserF(self, user):
    self.request.session[USER_TOKEN] = user
    self.user = user



class ContactsUserModel(Mapping):
    Users = ListField(DictField(UserModel))
    Companies = ListField(DictField(CompanyModel))
