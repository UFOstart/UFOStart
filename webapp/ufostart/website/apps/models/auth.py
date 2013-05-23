from hnc.apiclient import Mapping, TextField, IntegerField
from hnc.apiclient.backend import ClientTokenProc, DBNotification
import simplejson


class NewUserMsg(DBNotification): pass
class EmailTakenMsg(DBNotification): pass
class FbIdTakenMsg(DBNotification): pass
class UnknownUserMsg(DBNotification): pass

class UserModel(Mapping):
    token = TextField()
    name = TextField()
    pwd = TextField()
    email = TextField()

    def isAnon(self):
        return self.token is None
    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True).copy()
        return simplejson.dumps(json) if stringify else json


def AnonUser():
    return UserModel()


def LoggingInProc(path, db_messages = []):
    sproc = ClientTokenProc(path, root_key='User', result_cls=UserModel)
    def f(request, data):
        result = sproc(request, data)
        request.root.setUser(result)
        return result
    return f


WebSignupEmailProc = LoggingInProc("/web/user/signup", db_messages = {'EMAIL_TAKEN':EmailTakenMsg})
WebLoginEmailProc = LoggingInProc("/web/user/login")
PasswordRequestProc = ClientTokenProc("/web/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/web/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/web/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/web/user/token", root_key = "User", result_cls = UserModel)
CheckEmailExistsProc = ClientTokenProc('/web/user/emailavailable')


SocialConnectProc = LoggingInProc('/web/user/connect', db_messages={'UNKNOWN_USER':UnknownUserMsg})
RefreshAccessTokenProc= ClientTokenProc('/web/user/refreshAccessToken')
DisconnectFacebookProc = ClientTokenProc("/web/user/disconnectFb")
