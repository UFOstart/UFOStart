from importlib import import_module

from formencode.validators import StringBool
from hnc.tools.oauth import Consumer
from hnc.tools.routing import FunctionRoute, route_factory, App
from pyramid.decorator import reify
import simplejson

from . import contexts, index, auth, company, expert, user
from ufostart.website.apps.social import SocialLoginFailed, SocialLoginSuccessful


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute    ("website_index"                      , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")
]



class SocialNetworkSettings(object):
    http_options = {'disable_ssl_certificate_validation' : True}
    default_picture = "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def __init__(self, module, network, appid, appsecret, **kwargs):
        self.module = module
        self.network = network
        self.appid = appid
        self.appsecret = appsecret
        for k,v in kwargs.items():
            setattr(self, k, v)

    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)

class WebsiteSettings(object):
    key = "website"
    css_name = 'site'
    networks = {}

    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        self.trackUsers = StringBool().to_python(settings['trackUsers'])
        self.gaCode = settings['gaCode']

        networks = settings['network']
        for network, params in networks.items():
            moduleName = params.pop('module')
            module = import_module(moduleName)
            self.networks[network] = SocialNetworkSettings(module.SocialResource, network=network, **params)



    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

    config.add_view(auth.social.login , context = contexts.WebsiteRootContext, name = 'login', renderer = "ufostart:website/templates/auth/login.html")
    config.add_view(index.logout      , context = contexts.WebsiteRootContext, name = 'logout')

    config.include("ufostart.website.apps.company")
    config.include("ufostart.website.apps.user")
    config.include("ufostart.website.apps.auth")
    config.include("ufostart.website.apps.social")
