from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, STANDARD_VIEW_ATTRS, JSON_FORM_ATTRS

from . import contexts, index, auth
from .auth import fb

__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute   ("website_signup"                       , "/signup", contexts.WebsiteRootContext, auth.SignupHandler, "auth/signup.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, auth.logout, None)
    , FunctionRoute('website_join_checkemail'              , '/user/join/checkemail', contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , ClassRoute   ('website_password_forget'              , '/ajax/templates/password.html', contexts.WebsiteRootContext, auth.WebsitePasswordForgotHandler, "ajax/auth/password.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_reset_password'               , '/user/password/reset/:token', contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/password_reset.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_fblogin'                      , '/user/fb/login', contexts.WebsiteRootContext, fb.fb_login, "json", route_attrs = {"xhr":True})
    , FunctionRoute('website_fbtokenrefresh'               , '/user/fb/token/refresh', contexts.WebsiteRootContext, fb.fb_token_refresh, "json", route_attrs = {"xhr":True})
]
class WebsiteSettings(object):
    key = "website"
    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        self.fbAppId=settings['fbappid']
        self.fbAppSecret=settings['fbappsecret']

ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

