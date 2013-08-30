from importlib import import_module

from formencode.validators import StringBool
from hnc.tools.oauth import Consumer
from pyramid.decorator import reify
import simplejson

from . import contexts, index, auth, company, expert, user
from ufostart.handlers.social import SocialLoginFailed, SocialLoginSuccessful


__author__ = 'Martin'



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
    static_prefix = "/static/"
    networks = {}

    def __init__(self, settings):
        self.site_root_url = settings['site_root_url']
        self.clientToken = settings['apiToken']
        self.trackUsers = StringBool().to_python(settings['trackUsers'])
        self.gaCode = settings['gaCode']
        self.filepickerKey = settings['filepickerKey']

        networks = settings['network']
        for network, params in networks.items():
            moduleName = params.pop('module')
            module = import_module(moduleName)
            self.networks[network] = SocialNetworkSettings(module.SocialResource, network=network, **params)



    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)


    config.add_view(index.index       , context = contexts.WebsiteRootContext                , renderer = "ufostart:templates/index.html")
    config.add_view(auth.social.login , context = contexts.WebsiteRootContext, name = 'login', renderer = "ufostart:templates/auth/login.html")
    config.add_view(index.logout      , context = contexts.WebsiteRootContext, name = 'logout')

    config.include("ufostart.handlers.company")
    config.include("ufostart.handlers.user")
    config.include("ufostart.handlers.auth")
    config.include("ufostart.handlers.social")
