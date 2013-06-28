from importlib import import_module
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS, OAuthClassRoute, OAuthLoginRoute, TraversalRoute

from . import contexts, index, auth, company, expert, user
import simplejson
from ufostart.website.apps.social import SocialLoginFailed, SocialLoginSuccessful


__author__ = 'Martin'




ROUTE_LIST = [
    FunctionRoute    ("website_index"                      , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")
    , OAuthLoginRoute('website_login'                      , '/login', contexts.WebsiteRootContext                                           , auth.social.login, 'auth/login.html')
    , FunctionRoute  ('website_logout'                     , '/user/logout', contexts.WebsiteRootContext                                     , index.logout, None)

    , FunctionRoute  ("website_company_import_start"       , "/angellist/import/start", contexts.WebsiteRootContext                          , company.imp.company_import_start, "company/import/list.html")
    , FunctionRoute  ("website_company_import"             , "/angellist/import", contexts.WebsiteRootContext                                , company.imp.company_import, "company/import/list.html")
    , FunctionRoute  ("website_company_import_list"        , "/angellist/import/:user_id/:token", contexts.WebsiteRootContext                , company.imp.company_import_list, "company/import/list.html")
    , FunctionRoute  ("website_company_import_confirm"     , "/angellist/import/confirm/:company_id/:token", contexts.WebsiteRootContext     , company.imp.company_import_confirm, None)

    , OAuthLoginRoute("website_invite_confirm"             , '/invite/:token/confirm', contexts.WebsiteRootContext                           , company.invite.confirm, "company/invite_confirm.html")
    , OAuthLoginRoute("website_invite_answer"              , '/invite/:token', contexts.WebsiteRootContext                                   , company.invite.answer, "company/invite_confirm.html")
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
    config.include("ufostart.website.apps.company")
    config.include("ufostart.website.apps.user")
