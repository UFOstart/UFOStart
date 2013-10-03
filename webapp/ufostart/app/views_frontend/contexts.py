import logging, urllib, simplejson
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, Authenticated


from ufostart.lib.baseviews import RootContext
from ufostart.app.views_admin import AdminContext
from ufostart.app.views_frontend.auth import signup
from ufostart.app.views_frontend.auth import SocialContext, SignupContext
from ufostart.app.views_frontend.company import TemplatesRootContext, ProtoInviteContext, CompanyContext
from ufostart.app.views_frontend.user import UserProfileContext
from ufostart.app.models.auth import AnonUser, getUser, setUserF, USER_TOKEN
from ufostart.app.models.procs import CheckSlugProc

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
