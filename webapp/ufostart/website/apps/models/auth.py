from hnc.apiclient import Mapping, TextField, IntegerField, ListField, DictField
from pyramid.decorator import reify
import simplejson
from ufostart.website.apps.models.company import CompanyModel
from ufostart.website.apps.social import SocialNetworkProfileModel


SOCIAL_NETWORK_TYPES = {'LI':'linkedin', 'FB':'facebook', 'AL':'angellist', 'XI':'xing', 'TW':'twitter'}
SOCIAL_NETWORK_TYPES_REVERSE = {v:k for k,v in SOCIAL_NETWORK_TYPES.items()}



class WebUserNetworkProfile(SocialNetworkProfileModel):
    type = TextField()




class UserModel(Mapping):
    token = TextField()
    name = TextField()
    pwd = TextField()
    email = TextField()
    picture = TextField()
    Profile = ListField(DictField(WebUserNetworkProfile))
    Company = DictField(CompanyModel)
    Companies = ListField(DictField(CompanyModel))

    def isAnon(self):
        return self.token is None
    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True).copy()
        json.pop("Profile")
        json['networks'] = self.getSocialProfileJSON(False)
        return simplejson.dumps(json) if stringify else json

    def getSocialProfileJSON(self, stringify = True):
        result = {n.network:n.unwrap(sparse = True) for n in self.Profile if n.id}
        return simplejson.dumps(result) if stringify else result
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
    def profileMap(self):
        return {n.network:n for n in self.Profile}

    @property
    def position(self):
        return 'Expert'

def AnonUser():
    return UserModel()

