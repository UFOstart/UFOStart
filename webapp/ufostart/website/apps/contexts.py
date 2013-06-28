import logging
import urllib
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone
import simplejson
from ufostart.lib.baseviews import RootContext
from ufostart.website.apps.company import ProtoCompanyContext, TemplatesRootContext
from ufostart.website.apps.models.auth import AnonUser
from ufostart.website.apps.user import UserHomeContext, UserProtoContext

USER_SESSION_KEY = 'WEBSITE_USER'

log = logging.getLogger(__name__)



class WebsiteRootContext(RootContext):
    __name__ = None
    __parent__ = None
    __acl__ = [(Allow, Everyone, 'view')]

    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def user(self):
        return self.request.session.get(USER_SESSION_KEY) or AnonUser()

    def setUser(self, user):
        self.request.session[USER_SESSION_KEY] = self.user = user
        return user

    def logout(self):
        if USER_SESSION_KEY in self.request.session:
            del self.request.session[USER_SESSION_KEY]
        self.user = AnonUser()

    def getPostLoginUrlParams(self):
        user = self.user
        route, args, kwargs = "website_index", [], {}
        if user.Company and user.Company.slug:
            return "website_company", [], {'slug':user.Company.slug}
        if route != self.request.matched_route.name:
            return route, args, kwargs
        else:
            return None, None, None

    @reify
    def location(self):
        cache = self.request.globals.cache
        ip = self.request.client_addr
        location = cache.get('HOSTIP_{}'.format(ip))
        if not location:
            try:
                response = urllib.urlopen('http://api.hostip.info/get_json.php?ip={}&position=true'.format(ip)).read()
                result = simplejson.loads(response)
                location = '{city}, {country_name}'.format(**result)
                cache.set('HOSTIP_{}'.format(self.request.client_addr), location)
            except:
                pass
        return location

    def __getitem__(self, item):
        if item == 'c':
            return ProtoCompanyContext(self, 'c')
        elif item == 'u':
            return UserProtoContext(self, 'user')
        elif item == 'template':
            return TemplatesRootContext(self, 'template')
        elif item == 'home':
            return UserHomeContext(self, 'user', self.user.token)
        if item in self.settings.networks:
            return self.settings.networks[item]




    @property
    def template_select_url(self):
        return self.request.resource_url(self, 'template')
    def template_url(self, slug):
        return self.request.resource_url(self, 'template', slug)
    def company_url(self, slug):
        return self.request.resource_url(self, 'c', slug)
    def need_url(self, company_slug, need_slug):
        return self.request.resource_url(self, 'c', company_slug, 1, need_slug)

    def product_url(self, slug):
        return self.request.resource_url(self, 'c', slug, 1, 'product')
    def auth_url(self, network):
        return self.request.resource_url(self, 'login', network, query = [('furl', self.request.url)])

    def profile_url(self, token):
        request = self.request
        if token == self.user.token:
            return request.resource_url(self, 'home')
        else:
            return request.resource_url(self, 'u', token)