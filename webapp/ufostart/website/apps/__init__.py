from importlib import import_module
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS, BaseRoute, OAuthClassRoute, OAuthLoginRoute

from . import contexts, index, auth, company, expert, user
import simplejson
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.social import SocialLoginFailed, SocialLoginSuccessful


__author__ = 'Martin'




ROUTE_LIST = [
    FunctionRoute    ("website_index"                      , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")
    , OAuthLoginRoute('website_login'                      , '/login', contexts.WebsiteRootContext                                           , auth.social.login, 'auth/login.html')
    , FunctionRoute  ('website_logout'                     , '/user/logout', contexts.WebsiteRootContext                                     , index.logout, None)

    , OAuthLoginRoute('website_user_home'                  , '/home', contexts.WebsiteRootContext                                            , user.index.home, "user/home.html")
    , FunctionRoute  ('website_user'                       , '/u/:slug', contexts.WebsiteRootContext                                         , user.index.user, "user/home.html")

    , FunctionRoute  ('website_template_basic'             , '/templates', contexts.WebsiteRootContext                                       , company.setup.basics, "company/setup/basic.html")                #   Step 1
    , FunctionRoute  ('website_template_details'           , '/template/:template', contexts.WebsiteRootContext                              , company.setup.details, "company/setup/details.html")             #   Step 2
    , OAuthClassRoute('website_template_create'            , '/setup/:template', contexts.WebsiteRootContext                                 , company.setup.CreateProjectHandler, 'company/setup/create.html', view_attrs = JSON_FORM_ATTRS) #   Step 3

    , FunctionRoute  ('website_company'                    , '/c/:slug', contexts.WebsiteCompanyContext                                      , company.general.index, None)
    , ClassRoute     ("website_company_company"            , "/c/:slug/company", contexts.WebsiteCompanyContext                              , company.invite.InviteCompanyHandler, "company/company.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute     ("website_company_product"            , "/c/:slug/product", contexts.WebsiteCompanyContext                              , company.product.ProductOfferHandler, "company/product/index.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute     ("website_company_product_create"     , "/c/:slug/product/create", contexts.WebsiteCompanyContext                       , company.product.ProductCreateHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute     ("website_company_product_edit"       , "/c/:slug/product/edit", contexts.WebsiteCompanyContext                         , company.product.ProductEditHandler, "company/product/create.html", view_attrs = JSON_FORM_ATTRS)
    , OAuthLoginRoute('website_company_product_pledge'     , '/c/:slug/pledge', contexts.WebsiteCompanyContext                               , company.product.login, 'auth/login.html')

    , OAuthLoginRoute("website_round_approve_ask"          , '/c/:slug/askforapproval', contexts.WebsiteCompanyContext                              , company.general.ask_for_approval, None)
    , OAuthLoginRoute("website_round_publish"              , '/c/:slug/publish', contexts.WebsiteCompanyContext                              , company.general.publish_round, None)

    , FunctionRoute  ("website_company_import_start"       , "/angellist/import/start", contexts.WebsiteRootContext                          , company.imp.company_import_start, "company/import/list.html")
    , FunctionRoute  ("website_company_import"             , "/angellist/import", contexts.WebsiteRootContext                                , company.imp.company_import, "company/import/list.html")
    , FunctionRoute  ("website_company_import_list"        , "/angellist/import/:user_id/:token", contexts.WebsiteRootContext                , company.imp.company_import_list, "company/import/list.html")
    , FunctionRoute  ("website_company_import_confirm"     , "/angellist/import/confirm/:company_id/:token", contexts.WebsiteRootContext     , company.imp.company_import_confirm, None)

    , OAuthLoginRoute("website_invite_confirm"             , '/invite/:token/confirm', contexts.WebsiteRootContext                           , company.invite.confirm, "company/invite_confirm.html")
    , OAuthLoginRoute("website_invite_answer"              , '/invite/:token', contexts.WebsiteRootContext                                   , company.invite.answer, "company/invite_confirm.html")

    # NOTE: this will catch anything /c/:slug/....
    , ClassRoute     ("website_round_need_create"          , '/c/:slug/need/create', contexts.WebsiteCompanyContext                          , company.need.NeedCreateHandler, "company/need/create.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute     ("website_round_need_edit"            , '/c/:slug/:need/edit', contexts.WebsiteCompanyFounderContext                    , company.need.NeedEditHandler, "company/need/edit.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute  ("website_round_need"                 , '/c/:slug/:need', contexts.WebsiteCompanyContext                                , company.need.index, "company/need/index.html")
    , OAuthClassRoute("website_round_need_apply"           , '/c/:slug/:need/apply', contexts.WebsiteCompanyContext                          , company.need.ApplicationHandler, "company/need/apply.html", view_attrs = JSON_FORM_ATTRS)



    # , FunctionRoute('website_social_login'                 , '/social/:network/:action', contexts.WebsiteRootContext                         , auth.social.login, None)
    # , ClassRoute   ("website_company_basic"                , "/company/setup", contexts.WebsiteRootContext                                   , company.general.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)
    # , FunctionRoute('website_company_round_create'         , '/c/:slug/create/round', contexts.WebsiteCompanyContext                         , company.general.create_round, None)
    # , FunctionRoute("website_company_pledge_decide"        , "/c/:slug/pledge", contexts.WebsiteCompanyContext                               , company.customers.pledge_decide, "company/customers/pledge_decide.html")
    # , FunctionRoute('website_login_to_pledge'              , '/c/:slug/pledge/:network/:action', contexts.WebsiteCompanyContext              , company.customers.login, None)
    # , FunctionRoute('website_company_round_view'           , '/c/:slug/tasks', contexts.WebsiteCompanyContext                                , company.tasks.index, "company/tasks/index.html")
    # , FunctionRoute("website_expert_dashboard"             , '/expert/dashboard', contexts.WebsiteAuthedContext                              , expert.index.index, "expert/index.html")
]






class WebsiteSettings(object):
    key = "website"
    networks = {}

    def __init__(self, settings):
        self.clientToken = settings['apiToken']

        networks = settings['network']
        for network, params in networks.items():
            moduleName = params.pop('module')
            module = import_module(moduleName)
            self.networks[network] = module.SocialResource(network=network, **params)



    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

