import base64
import hashlib
import hmac
from operator import methodcaller
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, STANDARD_VIEW_ATTRS, JSON_FORM_ATTRS

from . import contexts, index, auth, company
import simplejson
from .auth import social
from ufostart.website.apps.auth.network_settings import SOCIAL_CONECTORS_MAP


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute   ("website_signup_decision"              , "/decide", contexts.WebsiteRootContext, auth.DecisionHandler, "auth/decide.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_company_basic"                , "/company/basics", contexts.WebsiteRootContext, company.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)


    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, auth.logout, None)
    , FunctionRoute('website_social_login'                 , '/user/login/social', contexts.WebsiteRootContext, social.social_login, "json", route_attrs = {"xhr":True})
    , FunctionRoute('website_social_login_start'           , '/social/:network', contexts.WebsiteRootContext, social.social_login_start, None)
    , FunctionRoute('website_social_login_callback'        , '/social/cb/:network', contexts.WebsiteRootContext, social.social_login_callback, None)


    , FunctionRoute('website_fbtokenrefresh'               , '/user/fb/token/refresh', contexts.WebsiteRootContext, social.fb_token_refresh, "json", route_attrs = {"xhr":True})

    , ClassRoute   ('website_company_setup_basic'          , '/company/setup/basic', contexts.WebsiteAuthedContext, company.setup.BasicHandler, "company/setup/template.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_company_setup_round'          , '/company/setup/round', contexts.WebsiteAuthedContext, company.setup.RoundHandler, "company/setup/needs.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company_round_view'           , '/company/round/:token', contexts.WebsiteAuthedContext, company.setup.show_latest_round, "company/round.html")

    , FunctionRoute('website_company'                      , '/company', contexts.WebsiteAuthedContext, company.general.index, "company/index.html")


    # NOTE: DEPRECATED
    , ClassRoute   ("website_signup"                       , "/signup", contexts.WebsiteAuthContext, auth.SignupHandler, "auth/signup.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute("website_require_li"                   , "/require/linked", contexts.WebsiteRootContext, auth.require_li, "auth/require_li.html")
    , FunctionRoute('website_join_checkemail'              , '/signup/checkemail', contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , ClassRoute   ('website_password_forget'              , '/ajax/templates/password.html', contexts.WebsiteRootContext, auth.WebsitePasswordForgotHandler, "ajax/auth/password.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_reset_password'               , '/user/password/reset/:token', contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/password_reset.html", view_attrs = JSON_FORM_ATTRS)
]



class WebsiteSettings(object):
    key = "website"
    networks = {}

    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        socials = map(methodcaller("strip"), settings['social_networks'].split(","))
        for network in socials:
            SettingsCls = SOCIAL_CONECTORS_MAP[network]
            self.networks[network] = SettingsCls(type=network, **settings[network])

    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

