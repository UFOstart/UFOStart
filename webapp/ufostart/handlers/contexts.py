import logging
import urllib
from hnc.apiclient.cached import CachedLoader
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, Authenticated
import simplejson
from ufostart.handlers.auth import signup
from ufostart.lib.baseviews import RootContext
from ufostart.admin import AdminContext
from ufostart.handlers.auth import SocialContext, SignupContext
from ufostart.handlers.company import TemplatesRootContext, ProtoInviteContext, CompanyContext
from ufostart.handlers.user import UserProfileContext
from ufostart.models.auth import AnonUser, getUser, setUserF, USER_TOKEN
from ufostart.admin.auth import isAdminUser
from ufostart.models.procs import CheckSlugProc, GetStaticContentProc

log = logging.getLogger(__name__)



ROOT_NAVIGATION = {
        'template':TemplatesRootContext
        , 'signup': SignupContext
        , 'login': SocialContext
        , 'invite': ProtoInviteContext
        , 'admin': AdminContext
    }

if len(set(ROOT_NAVIGATION.keys()).union(signup.RESERVEDS)) != len(signup.RESERVEDS):
    signup.RESERVEDS = ROOT_NAVIGATION.keys()

CHILD_CONTEXT_MAPPING = {
        'COMPANY': CompanyContext
        , 'USER': UserProfileContext
    }
def getContextFromSlug(childSlug):
    try:
        return CHILD_CONTEXT_MAPPING[childSlug.type]
    except AttributeError, e:
        raise KeyError(e.message)





def get_static_content(request):
    result = GetStaticContentProc(request)
    return {k.key:k.value for k in result.Static}
cache = CachedLoader(get_static_content, "WEBSITE_STATIC_CONTENT")

class StaticContentLoader(object):

    def __init__(self, request, debug, admin):
        self.content = cache.get(request)
        self.debug = debug
        self.admin = admin
        super(StaticContentLoader, self).__init__()

    def refresh(self, request):
        cache.refresh(request)

    def __call__(self, key, display_default = True):
        result = self.content.get(
                    key
                    , '###{}###'.format(key) if display_default else  ''
                )
        if self.debug:
            return '<!-- {} -->{}'.format(key, result)
        else:
            return result






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
    def static_content(self):
        req = self.request
        return StaticContentLoader(req, req.globals.is_debug, isAdminUser(req))


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


    children = ROOT_NAVIGATION

    def __getitem__(self, item):
        if item in self.children:
            return self.children[item](self, item)
        elif item in self.settings.networks:
            settings = self.settings.networks[item]
            return settings.module(self, item, settings)
        else:
            ctxt_cls = getContextFromSlug(CheckSlugProc(self.request, {'slug': item}))
            return ctxt_cls(self, item)



    def admin_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'admin', *args, **kwargs)


    def login_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'login', *args, **kwargs)
    def signup_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'signup', *args, **kwargs)
    def logout_url(self, *args, **kwargs):
        return self.request.resource_url(self, 'logout', *args, **kwargs)
    def auth_url(self, network):
        return self.request.resource_url(self, 'login', network, query = [('furl', self.request.url)])


    @property
    def home_url(self):
        return self.request.resource_url(self)
    @property
    def template_select_url(self):
        return self.request.resource_url(self, 'template')
    def template_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, 'template', slug, *args, **kwargs)


    def profile_url(self, slug):
        return self.request.resource_url(self, slug)
    def company_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, slug, *args, **kwargs)
    def round_url(self, slug, round_no = '1', *args, **kwargs):
        return self.request.resource_url(self, slug, round_no, *args, **kwargs)
    def need_url(self, company_slug, need_slug, *args, **kwargs):
        return self.request.resource_url(self, company_slug, 1, need_slug, *args, **kwargs)
    def product_url(self, slug, *args, **kwargs):
        return self.request.resource_url(self, slug, 1, 'product', *args, **kwargs)

    @property
    def angellist_url(self):
        return self.request.resource_url(self, 'angellist', query = [('furl', self.request.url)])
