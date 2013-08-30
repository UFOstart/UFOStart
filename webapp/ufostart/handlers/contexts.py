import logging
import urllib
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, Authenticated
import simplejson
from ufostart.lib.baseviews import RootContext
from ufostart.admin import AdminContext
from ufostart.handlers.auth import SocialContext, SignupContext
from ufostart.handlers.company import ProtoCompanyContext, TemplatesRootContext, ProtoInviteContext
from ufostart.handlers.user import UserHomeContext, UserStubContext
from ufostart.models.auth import AnonUser, getUser, setUserF, USER_TOKEN

log = logging.getLogger(__name__)


class WebsiteRootContext(RootContext):
    __name__ = None
    __parent__ = None
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'apply'), (Allow, Authenticated, 'join')]
    @property
    def site_title(self):
        return [self.request.globals.project_name]

    app_label = 'website'
    user = reify(getUser)
    setUser = setUserF

    def logout(self):
        if USER_TOKEN in self.request.session:
            del self.request.session[USER_TOKEN]
        self.user = AnonUser()


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


    children = {
        'c':ProtoCompanyContext
        , 'u':UserStubContext
        , 'template':TemplatesRootContext
        , 'home':UserHomeContext
        , 'signup': SignupContext
        , 'login': SocialContext
        , 'invite': ProtoInviteContext
        , 'admin': AdminContext
    }

    def __getitem__(self, item):
        if item in self.children:
            return self.children[item](self, item)
        elif item in self.settings.networks:
            settings = self.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            raise KeyError()



    def admin_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'admin', *args, **kwargs)


    def login_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'login', *args, **kwargs)
    def signup_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'signup', *args, **kwargs)
    def logout_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'logout', *args, **kwargs)


    @property
    def home_url(self):
        return self.request.resource_url(self)
    @property
    def template_select_url(self):
        return self.request.resource_url(self, 'template')
    def template_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, 'template', slug, *args, **kwargs)
    def company_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, 'c', slug, *args, **kwargs)
    def round_url(self, slug, round_no = '1', *args, **kwargs):
        return self.request.resource_url(self, 'c', slug, round_no, *args, **kwargs)
    def need_url(self, company_slug, need_slug, *args, **kwargs):
        return self.request.resource_url(self, 'c', company_slug, 1, need_slug, *args, **kwargs)
    def product_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, 'c', slug, 1, 'product', *args, **kwargs)
    def auth_url(self, network):
        return self.request.resource_url(self, 'login', network, query = [('furl', self.request.url)])
    @property
    def angellist_url(self):
        return self.request.resource_url(self, 'angellist', query = [('furl', self.request.url)])
    def profile_url(self, token):
        request = self.request
        if token == self.user.token:
            return request.resource_url(self, 'home')
        else:
            return request.resource_url(self, 'u', token)