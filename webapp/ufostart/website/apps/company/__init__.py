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
            raise KeyError()


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
    config.add_view(invite.InviteCompanyHandler             , context = CompanyContext    , renderer = "ufostart:website/templates/company/company.html")
    config.add_view(general.index                           , context = RoundContext      , renderer = "ufostart:website/templates/company/index.html")
    config.add_view(need.index                              , context = NeedContext       , renderer = "ufostart:website/templates/company/need/index.html")
    config.add_view(need.ApplicationHandler, name = 'apply' , context = NeedContext       , renderer = "ufostart:website/templates/company/need/apply.html")
    config.add_view(need.accept_application, name = 'accept', context = ApplicationContext)




    # , ClassRoute     ("website_company_company"            , "/c/:slug", contexts.WebsiteRootContext                                      , company.invite.InviteCompanyHandler, "company/company.html", view_attrs = JSON_FORM_ATTRS)
    # , FunctionRoute  ('website_company'                    , '/c/:slug/round', contexts.WebsiteRootContext                               , company.general.index, None)

    # , OAuthLoginRoute("website_round_publish"              , '/c/:slug/publish', contexts.WebsiteRootContext                       , company.general.publish_round, None)
    # , OAuthLoginRoute("website_round_approve_ask"          , '/c/:slug/askforapproval', contexts.WebsiteRootContext                , company.general.ask_for_approval, None)
    # , ClassRoute     ("website_company_add_mentor"         , "/c/:slug/mentor", contexts.WebsiteRootContext                        , company.invite.AddMentorHandler, "company/addmentor.html", view_attrs = JSON_FORM_ATTRS)
    # , ClassRoute     ("website_company_product"            , "/c/:slug/product", contexts.WebsiteRootContext                       , company.product.ProductOfferHandler, "company/product/index.html", view_attrs = JSON_FORM_ATTRS)
    # , ClassRoute     ("website_company_product_create"     , "/c/:slug/product/create", contexts.WebsiteRootContext                , company.product.ProductCreateHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    # , ClassRoute     ("website_company_product_edit"       , "/c/:slug/product/edit", contexts.WebsiteRootContext                  , company.product.ProductEditHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    # , OAuthLoginRoute('website_company_product_pledge'     , '/c/:slug/pledge', contexts.WebsiteRootContext                        , company.product.login, 'auth/login.html')
    #
    # , ClassRoute     ("website_round_need_create"          , '/c/:slug/need/create', contexts.WebsiteRootContext                   , company.need.NeedCreateHandler, "company/need/create.html", view_attrs = JSON_FORM_ATTRS)
    # , FunctionRoute  ("website_round_need"                 , '/c/:slug/:need', contexts.WebsiteRootContext                         , company.need.index, "company/need/index.html")
    # , ClassRoute     ("website_round_need_edit"            , '/c/:slug/:need/edit', contexts.WebsiteRootContext                    , company.need.NeedEditHandler, "company/need/edit.html", view_attrs = JSON_FORM_ATTRS)
    # , OAuthClassRoute("website_round_need_apply"           , '/c/:slug/:need/apply', contexts.WebsiteRootContext                   , company.need.ApplicationHandler, "company/need/apply.html", view_attrs = JSON_FORM_ATTRS)
    # , FunctionRoute  ("website_need_application_accept"    , '/c/:slug/:need/accept/:applicationToken', contexts.WebsiteRootContext, company.need.accept_application, "company/need/apply.html")
