from importlib import import_module

from formencode.validators import StringBool
from hnc.tools.oauth import Consumer
from pyramid.decorator import reify
import simplejson

from . import index, auth, company, expert, user
from ufostart.handlers.__resources__ import WebsiteRootContext
from ufostart.handlers.social import SocialLoginFailed, SocialLoginSuccessful


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
        self.gaDomain = settings['gaDomain']
        self.filepickerKey = settings['filepickerKey']

        networks = settings['network']
        for network, params in networks.items():
            moduleName = params.pop('module')
            module = import_module(moduleName)
            self.networks[network] = SocialNetworkSettings(module.SocialResource, network=network, **params)

        # so on startup time we know if it exists, it is very much required for the send button:
        self.fb_app_id = self.networks['facebook'].appid


    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)


    config.add_view(index.index       , context = WebsiteRootContext                , renderer = "ufostart:templates/index.html")
    config.add_view(auth.social.login , context = WebsiteRootContext, name='login'  , renderer = "ufostart:templates/auth/login.html")
    config.add_view(index.logout      , context = WebsiteRootContext, name='logout')
    config.add_view(index.content_view, context = WebsiteRootContext, name='content', renderer = "ufostart:templates/content.html")

    config.include("ufostart.handlers.company")
    config.include("ufostart.handlers.user")
    config.include("ufostart.handlers.auth")
    config.include("ufostart.handlers.social")
