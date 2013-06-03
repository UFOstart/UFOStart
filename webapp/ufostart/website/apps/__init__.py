from operator import methodcaller
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS

from . import contexts, index, auth, company
import simplejson
from ufostart.website.apps.social.angellist import AngelListSettings
from ufostart.website.apps.social.facebook import FacebookSettings
from ufostart.website.apps.social.linkedin import LinkedinSettings


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute   ("website_signup_decision"              , "/decide", contexts.WebsiteRootContext, auth.DecisionHandler, "auth/decide.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_company_basic"                , "/company/basics", contexts.WebsiteRootContext, company.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_company_invite"               , "/company/invite", contexts.WebsiteRootContext, company.InviteCompanyHandler, "company/invite.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company'                      , '/company', contexts.WebsiteAuthedContext, company.general.index, "company/index.html")


    , FunctionRoute("website_company_customers"            , "/company/customers", contexts.WebsiteAuthedContext, company.customers.index, None)
    , FunctionRoute("website_company_import"               , "/company/import/:network", contexts.WebsiteAuthedContext, company.customers.company_import, "company/customers/list.html")
    , FunctionRoute("website_company_import_list"          , "/company/import/:network/:user_id/:token", contexts.WebsiteAuthedContext, company.customers.company_import_list, "company/customers/list.html")
    , FunctionRoute("website_company_import_confirm"       , "/company/confirm/:network/:company_id/:token", contexts.WebsiteAuthedContext, company.customers.company_import_confirm, "company/customers/with_content_tmp.html")
    , FunctionRoute("website_company_pledge"               , "/company/pledge", contexts.WebsiteAuthedContext, company.customers.pledge_decide, "company/customers/pledge_decide.html")



    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, auth.logout, None)
    , FunctionRoute('website_social_login'                 , '/user/login/social', contexts.WebsiteRootContext, auth.social.social_login, "json", route_attrs = {"xhr":True})
    , FunctionRoute('website_social_login_start'           , '/social/:network', contexts.WebsiteRootContext, auth.social.social_login_start, None)
    , FunctionRoute('website_social_login_callback'        , '/social/cb/:network', contexts.WebsiteRootContext, auth.social.social_login_callback, None)


    , FunctionRoute('website_fbtokenrefresh'               , '/user/fb/token/refresh', contexts.WebsiteRootContext, auth.social.fb_token_refresh, "json", route_attrs = {"xhr":True})

    , ClassRoute   ('website_company_setup_basic'          , '/company/setup/basic', contexts.WebsiteAuthedContext, company.setup.BasicHandler, "company/setup/template.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_company_setup_round'          , '/company/setup/round', contexts.WebsiteAuthedContext, company.setup.RoundHandler, "company/setup/needs.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company_round_view'           , '/company/round/:token', contexts.WebsiteAuthedContext, company.setup.show_latest_round, "company/round.html")



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

