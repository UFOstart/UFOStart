from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, Authenticated, has_permission
from .tasks import *
import product, general, invite, need, imp, setup
from ufostart.website.apps.models.procs import GetCompanyProc


def canEdit(self): return has_permission('edit', self, self.request)
def canApprove(self): return has_permission('approve', self, self.request)



class ApplicationContext(object):
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)

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


class NeedContext(object):
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)

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


class RoundContext(object):
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)

    def __init__(self, parent, name, acl, round):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.request = parent.request
        self.round = round
    def __getitem__(self, item):
        if item in ['publish', 'askforapproval']: return None
        return NeedContext(self, item, self.__acl__, self.round.needMap[item])

    @reify
    def company(self):
        return self.__parent__.company


class CompanyContext(object):
    @reify
    def __acl__(self):
        mentors = [(Allow, 'u:%s' % u.token, 'approve') for u in self.company.Users if u.role == 'MENTOR']
        founders = [(Allow, 'u:%s' % u.token, 'edit') for u in self.company.Users if u.role == 'FOUNDER']
        return [(Allow, Authenticated, 'view')] + mentors + founders
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)

    def __init__(self, parent, name, company):
        self.__name__ = name
        self.__parent__ = parent
        self.company = company
        self.request = parent.request
        self.user = self.request.root.user
    def __getitem__(self, item):
        try:
            return RoundContext(self, int(item), self.__acl__, self.company.currentRound)
        except ValueError:
            pass


class ProtoCompanyContext(object):
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        self.request = parent.request

    def __getitem__(self, item):
        company = GetCompanyProc(self.request, {'slug': item})
        if not company: raise KeyError()
        else:
            return CompanyContext(self, item, company)

def includeme(config):
    config.add_view(invite.InviteCompanyHandler , context = CompanyContext                       , renderer = "ufostart:website/templates/company/company.html")
    config.add_view(invite.AddMentorHandler     , context = CompanyContext    , name='mentor'    , renderer = "ufostart:website/templates/company/addmentor.html")

    config.add_view(general.index               , context = RoundContext                         , renderer = "ufostart:website/templates/company/round.html")
    config.add_view(general.publish_round       , context = RoundContext      , name='publish'   , permission='approve')
    config.add_view(general.ask_for_approval    , context = RoundContext      , name='askforapproval'      , permission='edit')

    config.add_view(need.NeedCreateHandler      , context = RoundContext      , name='addneed'   , renderer = "ufostart:website/templates/company/need/create.html", permission='edit')

    config.add_view(need.index                  , context = NeedContext                          , renderer = "ufostart:website/templates/company/need/index.html")
    config.add_view(need.ApplicationHandler     , context = NeedContext       , name = 'apply'   , renderer = "ufostart:website/templates/company/need/apply.html")
    config.add_view(need.accept_application     , context = ApplicationContext, name = 'accept')
    config.add_view(need.NeedEditHandler        , context = NeedContext       , name = 'edit'    , renderer = "ufostart:website/templates/company/need/edit.html", permission='edit')



    # , ClassRoute     ("website_company_product"            , "/c/:slug/product", contexts.WebsiteRootContext                       , company.product.ProductOfferHandler, "company/product/index.html", view_attrs = JSON_FORM_ATTRS)
    # , ClassRoute     ("website_company_product_create"     , "/c/:slug/product/create", contexts.WebsiteRootContext                , company.product.ProductCreateHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    # , ClassRoute     ("website_company_product_edit"       , "/c/:slug/product/edit", contexts.WebsiteRootContext                  , company.product.ProductEditHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    # , OAuthLoginRoute('website_company_product_pledge'     , '/c/:slug/pledge', contexts.WebsiteRootContext                        , company.product.login, 'auth/login.html')
