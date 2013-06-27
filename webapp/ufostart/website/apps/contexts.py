import logging
import urllib
from pyramid.decorator import reify
import simplejson
from ufostart.lib.baseviews import RootContext
from ufostart.website.apps.company import ProtoCompanyContext
from ufostart.website.apps.models.auth import AnonUser

USER_SESSION_KEY = 'WEBSITE_USER'

log = logging.getLogger(__name__)



class WebsiteRootContext(RootContext):
    __name__ = None
    __parent__ = None

    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def user(self):
        return self.request.session.get(USER_SESSION_KEY) or AnonUser()
    def userURL(self, token):
        if token == self.user.token:
            return self.request.fwd_url("website_user_home")
        else:
            return self.request.fwd_url("website_user", slug = token)

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
        if item in self.settings.networks:
            return self.settings.networks[item]
