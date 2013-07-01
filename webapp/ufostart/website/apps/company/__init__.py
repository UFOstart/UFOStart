from hnc.apiclient.backend import DBNotification
from hnc.forms.messages import GenericErrorMessage
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import Allow, Everyone, Authenticated, has_permission
import product, general, invite, need, imp, setup
from ufostart.website.apps.models.procs import GetCompanyProc, GetTemplateDetailsProc, GetAllCompanyTemplatesProc, GetInviteDetailsProc


def canEdit(self): return has_permission('edit', self, self.request)
def canApprove(self): return has_permission('approve', self, self.request)


class BaseProjectContext(object):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'create')]
    __auth_template__ = "ufostart:website/templates/auth/login.html"
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)



class TemplateContext(BaseProjectContext):
    def __init__(self, parent, name, template):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request
        self.template = template


class TemplatesRootContext(BaseProjectContext):
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request


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
        self.request = parent.request
        self.application = application

    @reify
    def company(self):
        return self.__parent__.company
    @reify
    def round(self):
        return self.__parent__.round
    @reify
    def need(self):
        return self.__parent__.need


class NeedContext(BaseProjectContext):
    displayType = "Need"
    @property
    def displayName(self):
        return self.need.name


    def __init__(self, parent, name, acl, need):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.request = parent.request
        self.need = need
    def __getitem__(self, item):
        return ApplicationContext(self, item, self.__acl__, self.need.applicationMap[item])

    @reify
    def company(self):
        return self.__parent__.company
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
        self.request = parent.request
        self.product = product

    @reify
    def company(self):
        return self.__parent__.company
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
        self.request = parent.request
        self.round = round
    def __getitem__(self, item):
        if item in ['productsetup', 'publish', 'askforapproval']: raise KeyError()
        if item == 'product': return ProductContext(self, 'product', self.__acl__, self.round.Product)
        return NeedContext(self, item, self.__acl__, self.round.needMap[item])

    @reify
    def company(self):
        return self.__parent__.company


class CompanyContext(BaseProjectContext):
    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name

    @reify
    def __acl__(self):
        mentors = [(Allow, 'u:%s' % u.token, 'approve') for u in self.company.Users if u.role == 'MENTOR']
        founders = [(Allow, 'u:%s' % u.token, 'edit') for u in self.company.Users if u.role == 'FOUNDER']
        return [(Allow, Authenticated, 'view')] + mentors + founders

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request
        self.user = self.request.root.user

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
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request

    def __getitem__(self, item):
        return CompanyContext(self, item)





class InviteContext(BaseProjectContext):
    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name

    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'join')]
    __auth_template__ = "ufostart:website/templates/company/invite_confirm.html"

    canEdit = False
    canApprove = False

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request

    @reify
    def invite(self):
        invite = None
        try:
            invite = GetInviteDetailsProc(self.request, {'inviteToken': self.__name__})
        except DBNotification, e:
            pass
        if not invite:
            self.request.session.flash(GenericErrorMessage("Invalid Token, please check your email and link!"), "generic_messages")
            raise HTTPFound(self.request.home_url)
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
    __auth_template__ = "ufostart:website/templates/company/invite_confirm.html"
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request
    def __getitem__(self, item):
        return InviteContext(self, item)


def includeme(config):
    config.add_view(setup.basics                , context = TemplatesRootContext                 , renderer = "ufostart:website/templates/company/setup/basic.html")
    config.add_view(setup.details               , context = TemplateContext                      , renderer = "ufostart:website/templates/company/setup/details.html")
    config.add_view(setup.CreateProjectHandler  , context = TemplateContext   ,name = 'startcompany', renderer = "ufostart:website/templates/company/setup/create.html", permission = 'create')


    config.add_view(invite.CompanyIndexHandler  , context = CompanyContext                       , renderer = "ufostart:website/templates/company/company.html")
    config.add_view(setup.EditProjectHandler    , context = CompanyContext    , name='edit'      , renderer = "ufostart:website/templates/company/edit.html", permission = 'edit')

    config.add_view(invite.AddMentorHandler     , context = RoundContext      , name='mentor'    , renderer = "ufostart:website/templates/company/addmentor.html")
    config.add_view(general.index               , context = RoundContext                         , renderer = "ufostart:website/templates/company/round.html")
    config.add_view(general.publish_round       , context = RoundContext      , name='publish'   , permission='approve')
    config.add_view(general.ask_for_approval    , context = RoundContext      , name='askforapproval'  , permission='edit')

    config.add_view(product.ProductCreateHandler, context = RoundContext      , name='productsetup'  , renderer = "ufostart:website/templates/company/product/create.html", permission="edit")
    config.add_view(product.ProductOfferHandler , context = ProductContext                       , renderer = "ufostart:website/templates/company/product/index.html")
    config.add_view(product.ProductEditHandler  , context = ProductContext    , name='edit'      , renderer = "ufostart:website/templates/company/product/create.html", permission="edit")
    config.add_view(product.remove_offer        , context = ProductContext    , name='delete'    , renderer = "json", permission="edit")

    config.add_view(need.NeedCreateHandler      , context = RoundContext      , name='addneed'   , renderer = "ufostart:website/templates/company/need/create.html", permission='edit')
    config.add_view(need.index                  , context = NeedContext                          , renderer = "ufostart:website/templates/company/need/index.html")
    config.add_view(need.ApplicationHandler     , context = NeedContext       , name = 'apply'   , renderer = "ufostart:website/templates/company/need/apply.html")
    config.add_view(need.accept_application     , context = ApplicationContext, name = 'accept')
    config.add_view(need.NeedEditHandler        , context = NeedContext       , name = 'edit'    , renderer = "ufostart:website/templates/company/need/edit.html", permission='edit')


    config.add_view(invite.showInfo             , context = InviteContext                          , renderer = "ufostart:website/templates/company/invite_confirm.html", permission='join')
    config.add_view(invite.confirm              , context = InviteContext     , name = 'confirm'   , permission='join')
    config.add_view(invite.reject               , context = InviteContext     , name = 'reject'   , permission='join')


