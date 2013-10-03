from collections import OrderedDict
from hnc.apiclient.backend import DBNotification
from hnc.forms.messages import GenericErrorMessage
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import Allow, Everyone, Authenticated, has_permission
import product, general, need, setup, funding
from ufostart.app.views_frontend import t_path
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.models.procs import GetCompanyProc, GetTemplateDetailsProc, GetAllCompanyTemplatesProc, GetInviteDetailsProc



def canEdit(self): return has_permission('edit', self, self.request)
def canApprove(self): return has_permission('approve', self, self.request)


class BaseProjectContext(BaseContextMixin):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'create')]
    __auth_template__ = t_path("auth/login.html")
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)
    @property
    def site_title(self):
        return [self.displayName, self.company.display_name, self.request.globals.project_name]

    @reify
    def company(self):
        return self.__parent__.company


class TemplateContext(BaseProjectContext):
    @property
    def site_title(self):
        return [self.request.globals.project_name]
    def __init__(self, parent, name, template):
        self.__name__ = name
        self.__parent__ = parent
        self.template = template




class TemplatesRootContext(BaseProjectContext):
    @property
    def site_title(self):
        return [self.request.globals.project_name]
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, item):
        template = GetTemplateDetailsProc(self.request, {'key': item})
        if not template: raise KeyError()
        else:
            return TemplateContext(self, item, template)

    @reify
    def templates(self):
        return GetAllCompanyTemplatesProc(self.request)


class ApplicationContext(BaseProjectContext):
    displayType = "Application"
    displayName = ""

    def __init__(self, parent, name, acl, application):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.application = application

    @reify
    def round(self):
        return self.__parent__.round
    @reify
    def need(self):
        return self.__parent__.need


class NeedContext(BaseProjectContext):
    displayType = "Task"
    @property
    def displayName(self):
        return self.need.name


    def __init__(self, parent, name, acl, need):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.need = need
    def __getitem__(self, item):
        return ApplicationContext(self, item, self.__acl__, self.need.applicationMap[item])

    @reify
    def round(self):
        return self.__parent__.round

class ProductContext(BaseProjectContext):
    displayType = "Product"
    @property
    def displayName(self):
        return self.product.name

    def __init__(self, parent, name, acl, product):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.product = product

    @reify
    def round(self):
        return self.__parent__.round


class FundingContext(BaseProjectContext):
    displayType = 'Funding'
    displayName = 'Invest'

    def __init__(self, parent, name, acl, funding):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.funding = funding

    @reify
    def round(self):
        return self.__parent__.round

class RoundContext(BaseProjectContext):
    displayType = "Round"
    @property
    def displayName(self):
        return self.round.Template.name

    def __init__(self, parent, name, acl, round):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.round = round
    def __getitem__(self, item):
        if item in ['productsetup', 'approve', 'reject', 'askforapproval']: raise KeyError()
        if item == 'product': return ProductContext(self, 'product', self.__acl__, self.round.Product)
        if item == 'funding': return FundingContext(self, 'funding', self.__acl__, self.round.Funding)
        return NeedContext(self, item, self.__acl__, self.round.needMap[item])


    def groupedNeeds(self, n = 4, added = False):
        needs = [need for need in self.round.Needs if need.added == added]
        length = len(needs)
        if not length: return []
        result = OrderedDict()
        for i, need in enumerate(needs):
            l = result.setdefault(i % n, [])
            l.append(need)
        return result.values()




class CompanyContext(BaseProjectContext):
    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name
    @property
    def site_title(self):
        return [self.company.display_name, self.request.globals.project_name]


    @reify
    def __acl__(self):
        mentors = [(Allow, 'u:%s' % u.token, 'approve') for u in self.company.Users if u.isMentor]
        founders = [(Allow, 'u:%s' % u.token, 'edit') for u in self.company.Users]
        return [(Allow, Authenticated, 'view')] + mentors + founders


    def __getitem__(self, item):
        try:
            return RoundContext(self, int(item), self.__acl__, self.company.currentRound)
        except ValueError:
            raise KeyError()

    @reify
    def company(self):
        company = GetCompanyProc(self.request, {'slug': self.__name__})
        if not company: raise HTTPNotFound()
        else: return company

class ProtoCompanyContext(BaseProjectContext):

    def __getitem__(self, item):
        return CompanyContext(self, item)





class InviteContext(RoundContext):
    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name
    @property
    def site_title(self):
        return [self.company.display_name, self.request.globals.project_name]


    __auth_template__ = t_path("company/invite_confirm.html")

    canEdit = False
    canApprove = False

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        if self.company.isMember(self.request.root.user.token):
            raise HTTPFound(self.request.root.round_url(self.company.slug, '1'))

    @reify
    def mockContext(self):
        root = self.request.root
        protoCtxt = ProtoCompanyContext(root,'c')
        companyCtxt = CompanyContext(protoCtxt, self.company.slug)
        return RoundContext(companyCtxt,'1', companyCtxt.__acl__, self.company.Round)

    @reify
    def invite(self):
        invite = None
        try:
            invite = GetInviteDetailsProc(self.request, {'inviteToken': self.__name__})
        except DBNotification, e:
            pass
        if not invite:
            self.request.session.flash(GenericErrorMessage("Invalid Token, please check your email and link!"), "generic_messages")
            raise HTTPFound(self.request.root.home_url)
        return invite


    @reify
    def company(self):
        company = GetCompanyProc(self.request, {'slug': self.invite.companySlug})
        if not company: raise HTTPNotFound()
        else: return company

    @reify
    def round(self):
        return self.company.Round




class ProtoInviteContext(BaseProjectContext):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'join')]
    __auth_template__ = t_path("company/invite_confirm.html")
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, item):
        return InviteContext(self, item)




def includeme(config):

    config.add_view(setup.basics                , context = TemplatesRootContext                        , renderer = t_path("company/setup/basic.html"))
    config.add_view(setup.details               , context = TemplateContext                             , renderer = t_path("company/setup/details.html"))


    config.add_view(setup.CreateProjectHandler  , context = TemplateContext   , name = 'startcompany'   , renderer = t_path("company/company/create.html"), permission = 'create')
    config.add_view(general.CompanyIndexHandler , context = CompanyContext                              , renderer = t_path("company/company/index.html"))
    config.add_view(setup.EditProjectHandler    , context = CompanyContext    , name='edit'             , renderer = t_path("company/company/edit.html"), permission = 'edit')


    config.add_view(general.RoundDashboardHandler, context = RoundContext                               , renderer = t_path("company/round.html"))
    config.add_view(general.AddMentorHandler    , context = RoundContext      , name='mentor'           , renderer = t_path("company/addmentor.html"))
    config.add_view(general.add_top_mentor      , context = RoundContext      , name='topmentor'        , permission='edit')
    config.add_view(general.publish_round       , context = RoundContext      , name='approve'          , permission='approve')
    config.add_view(general.reject_round        , context = RoundContext      , name='reject'           , permission='approve')
    config.add_view(general.ask_for_approval    , context = RoundContext      , name='askforapproval'   , permission='edit')


    config.add_view(product.ProductCreateHandler, context = RoundContext      , name='productsetup'     , renderer = t_path("company/product/create.html"), permission="edit")
    config.add_view(product.ProductOfferHandler , context = ProductContext                              , renderer = t_path("company/product/index.html"))
    config.add_view(product.ProductEditHandler  , context = ProductContext    , name='edit'             , renderer = t_path("company/product/create.html"), permission="edit")
    config.add_view(product.remove_offer        , context = ProductContext    , name='delete'           , renderer = "json", permission="edit")


    config.add_view(funding.FundingCreateHandler, context = RoundContext      , name='fundingsetup'     , renderer = t_path("company/funding/create.html"), permission="edit")
    config.add_view(funding.InvestmentHandler   , context = FundingContext                              , renderer = t_path("company/funding/index.html"))
    config.add_view(funding.FundingEditHandler  , context = FundingContext    , name='edit'             , renderer = t_path("company/funding/edit.html"), permission='edit')


    config.add_view(need.NeedCreateHandler      , context = RoundContext      , name='new'              , renderer = t_path("company/need/create.html"), permission='edit')
    config.add_view(need.NeedIndexHandler       , context = NeedContext                                 , renderer = t_path("company/need/index.html"))
    config.add_view(need.ApplicationHandler     , context = NeedContext       , name = 'apply'          , renderer = t_path("company/need/apply.html"), permission='apply')
    config.add_view(need.accept_application     , context = ApplicationContext, name = 'accept')
    config.add_view(need.NeedEditHandler        , context = NeedContext       , name = 'edit'           , renderer = t_path("company/need/edit.html"), permission='edit')


    config.add_view(general.invite_landing      , context = InviteContext                               , renderer = t_path("company/invite_confirm.html"), permission='join')
    config.add_view(general.confirm             , context = InviteContext     , name = 'confirm'        , permission='join')
    config.add_view(general.reject              , context = InviteContext     , name = 'reject'         , permission='join')


