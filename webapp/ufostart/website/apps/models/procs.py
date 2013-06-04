from hnc.apiclient.backend import ClientTokenProc, DBNotification
from ufostart.website.apps.models.auth import UserModel
from ufostart.website.apps.models.company import RoundModel, CompanyModel


class NewUserMsg(DBNotification): pass
class EmailTakenMsg(DBNotification): pass
class FbIdTakenMsg(DBNotification): pass
class UnknownUserMsg(DBNotification): pass


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




#
################# USER AUTH
#

WebSignupEmailProc = LoggingInProc("/web/user/emailsignup")
WebLoginEmailProc = LoggingInProc("/web/user/login")
PasswordRequestProc = ClientTokenProc("/web/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/web/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/web/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/web/user/token", root_key = "User", result_cls = UserModel)
CheckEmailExistsProc = ClientTokenProc('/web/user/emailavailable')


SocialConnectProc = LoggingInProc('/web/user/connect', db_messages={'NEWUSER':NewUserMsg, 'FB_USER_WITH_CHANGED_EMAIL': NewUserMsg})
RefreshAccessTokenProc= ClientTokenProc('/web/user/refreshAccessToken')
DisconnectFacebookProc = ClientTokenProc("/web/user/disconnectFb")


#
################# COMPANY
#

CreateCompanyProc = LoggingInProc("/web/company/create")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)

CreateRoundProc = ClientTokenProc("/web/round/create", root_key="Round", result_cls=RoundModel)
GetRoundProc = ClientTokenProc("/web/round", root_key="Round", result_cls=RoundModel)

