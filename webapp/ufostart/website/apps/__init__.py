from hnctools.routing import ClassRoute, FunctionRoute, route_factory, App, STANDARD_VIEW_ATTRS

from . import contexts, index

__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute     ("website_index"             , "/", contexts.WebsiteRootContext, index.index, "index.html")
]
class WebsiteSettings(object):
    key = "website"
    def __init__(self, settings):
        self.fbAppId=settings['fbappid']
        self.fbAppSecret=settings['fbappsecret']

ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')