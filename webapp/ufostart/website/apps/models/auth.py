from hnc.apiclient import Mapping, TextField, IntegerField, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc, DBNotification
from pyramid.decorator import reify
import simplejson
from ufostart.website.apps.models.company import CompanyModel


class NewUserMsg(DBNotification): pass
class EmailTakenMsg(DBNotification): pass
class FbIdTakenMsg(DBNotification): pass
class UnknownUserMsg(DBNotification): pass


SOCIAL_NETWORK_TYPES = {'LI':'linkedin', 'FB':'facebook'}
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


def LoggingInProc(path, db_messages = {}):
    sproc = ClientTokenProc(path, root_key='User', result_cls=UserModel)
    def f(request, data):
        try:
            result = sproc(request, data)
        except DBNotification, e:
            error = db_messages.get(e.message)
            if error:
                user = UserModel.wrap(e.result.get("User"))
                request.root.setUser(user)
                return user
            else:
                raise e
        request.root.setUser(result)
        return result
    return f


WebSignupEmailProc = LoggingInProc("/web/user/emailsignup", db_messages = {'EMAIL_TAKEN':EmailTakenMsg})
WebLoginEmailProc = LoggingInProc("/web/user/login")
PasswordRequestProc = ClientTokenProc("/web/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/web/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/web/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/web/user/token", root_key = "User", result_cls = UserModel)
CheckEmailExistsProc = ClientTokenProc('/web/user/emailavailable')


SocialConnectProc = LoggingInProc('/web/user/connect', db_messages={'NEWUSER':NewUserMsg, 'FB_USER_WITH_CHANGED_EMAIL': NewUserMsg})
RefreshAccessTokenProc= ClientTokenProc('/web/user/refreshAccessToken')
DisconnectFacebookProc = ClientTokenProc("/web/user/disconnectFb")