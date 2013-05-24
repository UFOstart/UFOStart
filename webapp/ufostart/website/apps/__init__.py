import base64
import hashlib
import hmac
from operator import methodcaller
import urllib
from urlparse import parse_qsl
from hnc.tools.oauth import Consumer, Client
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, STANDARD_VIEW_ATTRS, JSON_FORM_ATTRS

from . import contexts, index, auth
import simplejson
from .auth import social


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute   ("website_signup"                       , "/signup", contexts.WebsiteRootContext, auth.SignupHandler, "auth/signup.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, auth.logout, None)
    , FunctionRoute('website_join_checkemail'              , '/signup/checkemail', contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , ClassRoute   ('website_password_forget'              , '/ajax/templates/password.html', contexts.WebsiteRootContext, auth.WebsitePasswordForgotHandler, "ajax/auth/password.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ('website_reset_password'               , '/user/password/reset/:token', contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/password_reset.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_social_login'                 , '/user/login/social', contexts.WebsiteRootContext, social.social_login, "json", route_attrs = {"xhr":True})
    , FunctionRoute('website_fbtokenrefresh'               , '/user/fb/token/refresh', contexts.WebsiteRootContext, social.fb_token_refresh, "json", route_attrs = {"xhr":True})
]


class SocialSettings(object):
    def __init__(self, type, appid, appsecret):
        self.type = type
        self.appid = appid
        self.appsecret = appsecret

    def toPublicJson(self, stringify = True):
        result = {'appId':self.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result

    def requiresAction(self):
        return self.type == 'linkedin'

    def action(self, request, profile):
        cookie = request.cookies.get('linkedin_oauth_{}'.format(self.appid))
        values = simplejson.loads(urllib.unquote(cookie))
        sig = hmac.new(str(self.appsecret), digestmod=hashlib.sha1)
        for key in values['signature_order']:
            sig.update(values[key])
        if values['signature'] != base64.b64encode(sig.digest()):
            raise social.InvalidSignatureException()

        consumer = Consumer(self.appid, self.appsecret)
        client = Client(consumer)
        status, response = client.request('https://api.linkedin.com/uas/oauth/accessToken', method="POST",body="xoauth_oauth2_access_token={}".format(values['access_token']))
        res = dict(parse_qsl(response))
        profile['access_token'] = res['oauth_token']
        profile['access_token_secret'] = res['oauth_token_secret']
        return profile


class WebsiteSettings(object):
    key = "website"

    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        socials = map(methodcaller("strip"), settings['social_networks'].split(","))
        self.networks = {k:SocialSettings(type=k, **settings[k]) for k in socials}

    def toPublicJson(self, stringify = True):
        result = {k:v.toPublicJson(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

