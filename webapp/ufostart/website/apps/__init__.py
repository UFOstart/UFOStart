from importlib import import_module
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS, BaseRoute, OAuthClassRoute, OAuthLoginRoute

from . import contexts, index, auth, company, expert
import simplejson
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.social import SocialLoginFailed, SocialLoginSuccessful


__author__ = 'Martin'




ROUTE_LIST = [
    FunctionRoute    ("website_index"                      , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")
    , OAuthLoginRoute('website_login'                      , '/login', contexts.WebsiteRootContext                                           , auth.social.login, 'auth/login.html')
    , FunctionRoute  ('website_logout'                     , '/user/logout', contexts.WebsiteRootContext                                     , index.logout, None)

    , FunctionRoute  ('website_template_basic'             , '/templates', contexts.WebsiteRootContext                                       , index.template.basics, "template/basic.html")        #   Step 1
    , FunctionRoute  ('website_template_details'           , '/template/:template', contexts.WebsiteRootContext                              , index.template.details, "template/details.html")     #   Step 2
    , OAuthLoginRoute('website_template_create'            , '/setup/:template', contexts.WebsiteRootContext                                 , index.template.create_project, None)                 #   Step 3


    , FunctionRoute('website_company'                      , '/c/:slug', contexts.WebsiteCompanyContext                                      , company.general.index, None)
    , ClassRoute   ("website_company_company"              , "/c/:slug/company", contexts.WebsiteCompanyContext                              , company.invite.InviteCompanyHandler, "company/company.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute("website_company_product"              , "/c/:slug/product", contexts.WebsiteCompanyContext                              , company.product.index, "company/product.html")

    , FunctionRoute("website_company_import_start"         , "/angellist/import/start", contexts.WebsiteCompanyFounderContext                , company.imp.company_import_start, "company/import/list.html")
    , FunctionRoute("website_company_import"               , "/angellist/import", contexts.WebsiteCompanyFounderContext                      , company.imp.company_import, "company/import/list.html")
    , FunctionRoute("website_company_import_list"          , "/c/:slug/import/:user_id/:token", contexts.WebsiteCompanyFounderContext        , company.imp.company_import_list, "company/import/list.html")
    , FunctionRoute("website_company_import_confirm"       , "/c/:slug/confirm/:company_id/:token", contexts.WebsiteCompanyFounderContext    , company.imp.company_import_confirm, None)

    , ClassRoute   ("website_round_need_create"            , '/c/:slug/need/create', contexts.WebsiteCompanyContext                          , company.need.NeedCreateHandler, "company/need/create.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_round_need_edit"              , '/c/:slug/:need/edit', contexts.WebsiteCompanyFounderContext                    , company.need.NeedEditHandler, "company/need/edit.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute("website_round_need"                   , '/c/:slug/:need', contexts.WebsiteCompanyContext                                , company.need.index, "company/need/index.html")
    ,OAuthClassRoute("website_round_need_apply"             , '/c/:slug/:need/apply', contexts.WebsiteCompanyContext                         , company.need.ApplicationHandler, "company/need/index.html", view_attrs = JSON_FORM_ATTRS)


    # , FunctionRoute('website_social_login'                 , '/social/:network/:action', contexts.WebsiteRootContext                         , auth.social.login, None)
    #
    # , ClassRoute   ("website_company_basic"                , "/company/setup", contexts.WebsiteRootContext                                   , company.general.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)
    #
    # , FunctionRoute('website_company_round_create'         , '/c/:slug/create/round', contexts.WebsiteCompanyContext                         , company.general.create_round, None)
    #
    #

    #
    # , FunctionRoute("website_company_pledge_decide"        , "/c/:slug/pledge", contexts.WebsiteCompanyContext                               , company.customers.pledge_decide, "company/customers/pledge_decide.html")
    # , FunctionRoute('website_login_to_pledge'              , '/c/:slug/pledge/:network/:action', contexts.WebsiteCompanyContext              , company.customers.login, None)
    #
    #
    # , FunctionRoute('website_company_round_view'           , '/c/:slug/tasks', contexts.WebsiteCompanyContext                                , company.tasks.index, "company/tasks/index.html")
    #
    #
    # , FunctionRoute("website_expert_dashboard"             , '/expert/dashboard', contexts.WebsiteAuthedContext                              , expert.index.index, "expert/index.html")

    #
    #
    # , FunctionRoute("website_invite_answer"                , '/invite/:token', contexts.WebsiteRootContext                                   , company.invite.answer, "company/invite_confirm.html")
    # , FunctionRoute("website_invite_confirm"               , '/invite/:token/confirm', contexts.WebsiteAuthedContext                         , company.invite.confirm, "company/invite_confirm.html")
    # , FunctionRoute('website_invite_login'                 , '/invite/login/:network/:action/:token', contexts.WebsiteRootContext            , company.invite.login, None)

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

