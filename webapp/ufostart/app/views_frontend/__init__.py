import simplejson

from importlib import import_module
from formencode.validators import StringBool
from pyramid.decorator import reify

from hnc.tools.oauth import Consumer

from . import contexts, index, auth, company, expert, user
from ufostart.app.views_frontend.social import SocialLoginFailed, SocialLoginSuccessful


def t_path(p): return "ufostart:templates_frontend/{}".format(p)


class BaseSettings(object):
    key = "website"
    css_name = 'site'
    static_prefix = "/static/"


class SocialNetworkSettings(BaseSettings):
    http_options = {'disable_ssl_certificate_validation' : True}
    default_picture = "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    static_prefix = "/static/"
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

class WebsiteSettings(BaseSettings):
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

    config.add_view(index.index       , context = contexts.WebsiteRootContext                , renderer = t_path("index.html"))
    config.add_view(auth.social.login , context = contexts.WebsiteRootContext, name = 'login', renderer = t_path("auth/login.html"))
    config.add_view(index.logout      , context = contexts.WebsiteRootContext, name = 'logout')

    config.include("ufostart.app.views_frontend.company")
    config.include("ufostart.app.views_frontend.user")
    config.include("ufostart.app.views_frontend.auth")
    config.include("ufostart.app.views_frontend.social")
