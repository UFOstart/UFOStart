from operator import methodcaller
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS

from . import contexts, index, auth, company
import simplejson
from ufostart.website.apps.social.angellist import AngelListSettings
from ufostart.website.apps.social.facebook import FacebookSettings
from ufostart.website.apps.social.linkedin import LinkedinSettings


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")

    , ClassRoute   ("website_signup_decision"              , "/decide", contexts.WebsiteRootContext                                          , auth.DecisionHandler, "auth/decide.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_social_login'                 , '/social/:network', contexts.WebsiteRootContext                                 , auth.social.social_login_start, None)
    , FunctionRoute('website_social_login_callback'        , '/social/cb/:network', contexts.WebsiteRootContext                              , auth.social.social_login_callback, None)


    , ClassRoute   ("website_company_basic"                , "/company/setup", contexts.WebsiteRootContext                                   , company.general.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_company_invite"               , "/c/:slug/invite", contexts.WebsiteCompanyContext                               , company.general.InviteCompanyHandler, "company/invite.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company'                      , '/c/:slug', contexts.WebsiteCompanyContext                                      , company.general.index, None)
    , FunctionRoute('website_company_round_create'         , '/c/:slug/create/round', contexts.WebsiteCompanyContext                         , company.general.create_round, None)


    , FunctionRoute("website_company_customers"            , "/c/:slug/customers", contexts.WebsiteCompanyContext                            , company.customers.index, None)
    , FunctionRoute("website_company_import"               , "/company/import/:network", contexts.WebsiteAuthedContext                       , company.customers.company_import, "company/customers/list.html")
    , FunctionRoute("website_company_import_list"          , "/c/:slug/import/:network/:user_id/:token", contexts.WebsiteCompanyContext      , company.customers.company_import_list, "company/customers/list.html")
    , FunctionRoute("website_company_import_confirm"       , "/c/:slug/confirm/:network/:company_id/:token", contexts.WebsiteCompanyContext  , company.customers.company_import_confirm, None)

    , FunctionRoute("website_company_pledge_decide"        , "/c/:slug/pledge", contexts.WebsiteCompanyContext                               , company.customers.pledge_decide, "company/customers/pledge_decide.html")
    , FunctionRoute('website_login_to_pledge'              , '/c/:slug/pledge/:network', contexts.WebsiteCompanyContext                      , company.customers.login_to_pledge, None)
    , FunctionRoute('website_login_to_pledge_callback'     , '/c/:slug/pledge/cb/:network', contexts.WebsiteCompanyContext                   , company.customers.login_to_pledge_callback, None)


    , FunctionRoute('website_company_setup_basic'          , '/c/:slug/tasks/template', contexts.WebsiteCompanyContext                       , company.tasks.needs_template_select, "company/tasks/template.html")
    , ClassRoute   ('website_company_setup_round'          , '/c/:slug/tasks/:template', contexts.WebsiteCompanyContext                      , company.tasks.TasksHandler, "company/tasks/needs.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company_round_view'           , '/c/:slug/tasks', contexts.WebsiteCompanyContext                                , company.tasks.index, "company/tasks/index.html")



    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, auth.logout, None)



    , FunctionRoute('website_fbtokenrefresh'               , '/user/fb/token/refresh', contexts.WebsiteRootContext, auth.social.fb_token_refresh, "json", route_attrs = {"xhr":True})


    # NOTE: DEPRECATED
    , ClassRoute   ("website_signup"                       , "/signup", contexts.WebsiteAuthContext, auth.SignupHandler, "auth/signup.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute("website_require_li"                   , "/require/linked", contexts.WebsiteRootContext, auth.require_li, "auth/require_li.html")
    , FunctionRoute('website_join_checkemail'              , '/signup/checkemail', contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , ClassRoute   ('website_password_forget'              , '/ajax/templates/password.html', contexts.WebsiteRootContext, auth.WebsitePasswordForgotHandler, "ajax/auth/password.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_reset_password'               , '/user/password/reset/:token', contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/password_reset.html", view_attrs = JSON_FORM_ATTRS)
]



SOCIAL_CONNECTORS_MAP = {'angellist': AngelListSettings, 'facebook': FacebookSettings, 'linkedin': LinkedinSettings}

class WebsiteSettings(object):
    key = "website"
    networks = {}

    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        socials = map(methodcaller("strip"), settings['social_networks'].split(","))
        for network in socials:
            SettingsCls = SOCIAL_CONNECTORS_MAP[network]
            self.networks[network] = SettingsCls(type=network, **settings[network])

    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

