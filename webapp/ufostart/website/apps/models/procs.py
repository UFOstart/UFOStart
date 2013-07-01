from hnc.apiclient.backend import ClientTokenProc, DBNotification
from ufostart.website.apps.models.auth import UserModel
from ufostart.website.apps.models.company import RoundModel, CompanyModel, NeedModel, TemplateModel, InviteModel


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

RefreshProfileProc = LoggingInProc("/web/user/profile")
GetProfileProc = ClientTokenProc("/web/user/profile", root_key = "User", result_cls = UserModel)

#
################# HOMEPAGE
#

FindPublicNeeds = ClientTokenProc("/web/need/search", result_cls=NeedModel, root_key="Needs", result_list=True)
FindPublicNeedsByLocation = ClientTokenProc("/web/need/location", result_cls=NeedModel, root_key="Needs", result_list=True)
GetPopularNeeds = ClientTokenProc("/web/need/popular", result_cls=NeedModel, root_key='Needs', result_list=True)
GetNewProductsProc = ClientTokenProc("/web/product/newest", root_key="Companies", result_cls=CompanyModel, result_list=True)

#
################# COMPANY
#

CreateCompanyProc = LoggingInProc("/web/company/create")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)
EditCompanyProc = ClientTokenProc("/web/company/edit", root_key="Company", result_cls=CompanyModel)
AddUpdateCompanyProc = ClientTokenProc("/web/company/update", root_key="Company", result_cls=CompanyModel)


CreateRoundProc = ClientTokenProc("/web/round/create", root_key="Round", result_cls=RoundModel)
GetRoundProc = ClientTokenProc("/web/round", root_key="Round", result_cls=RoundModel)

SetRoundTasksProc = ClientTokenProc("/web/round/needs")

CreateProductProc = ClientTokenProc("/web/product/create")
SetProductOffersProc = ClientTokenProc("/web/product/offer")

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)

PledgeCompanyProc = ClientTokenProc("/web/pledge/create")

GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateModel, root_key="Templates", result_list=True)
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)


SetCompanyAngelListPitchProc = ClientTokenProc("/web/company/angellist")
CreateNeedProc = ClientTokenProc("/web/round/needcreate", result_cls=NeedModel, root_key="Need")
EditNeedProc = ClientTokenProc("/web/round/need", result_cls=RoundModel, root_key="Round")
ApplyForNeedProc = ClientTokenProc("/web/need/application")
ApproveApplicationProc = ClientTokenProc("/web/need/approveapplication")

InviteToCompanyProc = ClientTokenProc("/web/company/invite")
GetInviteDetailsProc = ClientTokenProc("/web/company/getInvite", result_cls=InviteModel, root_key="Invite")
AcceptInviteProc = ClientTokenProc("/web/company/acceptInvite")


PublishRoundProc = ClientTokenProc("/web/round/publish")
AskForApprovalProc = ClientTokenProc("/web/round/sendmentor")

