from hnc.apiclient import Mapping, TextField, IntegerField, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc, DBNotification
from pyramid.decorator import reify
import simplejson
from ufostart.website.apps.models.company import CompanyModel



SOCIAL_NETWORK_TYPES = {'LI':'linkedin', 'FB':'facebook', 'AL':'angellist'}
SOCIAL_NETWORK_TYPES_REVERSE = {v:k for k,v in SOCIAL_NETWORK_TYPES.items()}




class SocialNetworkProfileModel(Mapping):
    id = TextField()
    type = TextField()
    picture = TextField()
    name = TextField()
    email = TextField()
    accessToken = TextField()
    def getTypeName(self):
        return SOCIAL_NETWORK_TYPES[self.type]


class UserModel(Mapping):
    token = TextField()
    name = TextField()
    pwd = TextField()
    email = TextField()
    picture = TextField()
    Profile = ListField(DictField(SocialNetworkProfileModel))
    Company = DictField(CompanyModel)

    def isAnon(self):
        return self.token is None
    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True).copy()
        json.pop("Profile")
        json['networks'] = self.getSocialProfileJSON(False)
        return simplejson.dumps(json) if stringify else json

    def getSocialProfileJSON(self, stringify = True):
        result = {n.getTypeName():n.unwrap(sparse = True) for n in self.Profile if n.id}
        return simplejson.dumps(result) if stringify else result

    @reify
    def profileMap(self):
        return {n.getTypeName():n for n in self.Profile}

def AnonUser():
    return UserModel()

