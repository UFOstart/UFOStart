from hnc.apiclient import Mapping, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc, DBNotification
from ufostart.models.tasks import NamedModel
from ufostart.models.auth import UserModel
from ufostart.models.company import RoundModel, CompanyModel, NeedModel, TemplateModel, InviteModel, ServiceModel


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

GetTopTags = ClientTokenProc("/web/tag/top20", root_key='Tags', result_cls=NamedModel, result_list=True)

#
################# COMPANY
#

CreateCompanyProc = LoggingInProc("/web/company/create")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)
EditCompanyProc = ClientTokenProc("/web/company/edit", root_key="Company", result_cls=CompanyModel)
AddUpdateCompanyProc = ClientTokenProc("/web/company/update", root_key="Company", result_cls=CompanyModel)


class MentorTempModel(Mapping): User = ListField(DictField(UserModel))
GetTopMentorsProc = ClientTokenProc("/web/mentor/top", root_key="Mentors", result_cls=MentorTempModel)

CreateRoundProc = ClientTokenProc("/web/round/create", root_key="Round", result_cls=RoundModel)
GetRoundProc = ClientTokenProc("/web/round", root_key="Round", result_cls=RoundModel)

CreateFundingProc = ClientTokenProc("/web/funding/create")
InvestInCompanyProc = ClientTokenProc("/web/funding/invest")

CreateProductProc = ClientTokenProc("/web/product/create", root_key="Round", result_cls=RoundModel)
SetProductOffersProc = ClientTokenProc("/web/product/offer")
RemoveProductOfferProc = ClientTokenProc("/web/product/offerDelete")

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
AddNeedToRound = ClientTokenProc("/web/round/needAdd")


InviteToCompanyProc = ClientTokenProc("/web/company/invite")
InviteToNeedProc = ClientTokenProc("/web/need/invite")
GetInviteDetailsProc = ClientTokenProc("/web/company/getInvite", result_cls=InviteModel, root_key="Invite")
AcceptInviteProc = ClientTokenProc("/web/company/acceptInvite")


PublishRoundProc = ClientTokenProc("/web/round/publish")
AskForApprovalProc = ClientTokenProc("/web/round/sendmentor")




#=================================================== Admin tool ==========================================================

AdminNeedCreateProc = ClientTokenProc("/admin/need/create", result_cls=NeedModel, root_key="Need")
AdminNeedEditProc = ClientTokenProc("/admin/need/edit", result_cls=NeedModel, root_key="Need")
AdminNeedGetProc = ClientTokenProc("/admin/need", result_cls=NeedModel, root_key="Need")
AdminNeedAllProc = ClientTokenProc("/admin/need/all", result_cls=NeedModel, root_key="Needs", result_list=True)

AdminServiceCreateProc = ClientTokenProc("/admin/service/create", result_cls=ServiceModel, root_key="Service")
AdminServiceEditProc = ClientTokenProc("/admin/service/edit", result_cls=ServiceModel, root_key="Service")
AdminServiceGetProc = ClientTokenProc("/admin/service", result_cls=ServiceModel, root_key="Service")
AdminServiceAllProc = ClientTokenProc("/admin/service/all", result_cls=ServiceModel, root_key="Services", result_list=True)

AdminTemplatesCreateProc = ClientTokenProc("/admin/template/create", result_cls=TemplateModel, root_key="Template")
AdminTemplatesEditProc = ClientTokenProc("/admin/template/edit", result_cls=TemplateModel, root_key="Template")
AdminTemplatesGetProc = ClientTokenProc("/admin/template", result_cls=TemplateModel, root_key="Template")
AdminTemplatesAllProc = ClientTokenProc("/admin/template/all", result_cls=TemplateModel, root_key="Templates", result_list=True)